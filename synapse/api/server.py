"""
FastAPI server for Project Synapse
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from ..core import FederatedIndexer, PrivacyAwareQueryEngine, KnowledgeSynthesizer
from ..security import DifferentialPrivacyManager, EncryptionManager
from .routes import router

logger = logging.getLogger(__name__)


# Global instances (in production, use dependency injection)
federated_indexer = None
query_engine = None
synthesizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global federated_indexer, query_engine, synthesizer
    
    logger.info("Starting Project Synapse server...")
    
    # Initialize core components
    privacy_manager = DifferentialPrivacyManager(global_privacy_budget=10.0)
    encryption_manager = EncryptionManager()
    
    federated_indexer = FederatedIndexer(privacy_manager=privacy_manager)
    query_engine = PrivacyAwareQueryEngine(federated_indexer)
    synthesizer = KnowledgeSynthesizer()
    
    # Store in app state for access in routes
    app.state.federated_indexer = federated_indexer
    app.state.query_engine = query_engine
    app.state.synthesizer = synthesizer
    app.state.privacy_manager = privacy_manager
    app.state.encryption_manager = encryption_manager
    
    logger.info("Project Synapse server started successfully")
    
    yield
    
    logger.info("Shutting down Project Synapse server...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Project Synapse",
        description="Cross-Silo Enterprise Knowledge Fabric",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "synapse"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "Project Synapse",
            "description": "Cross-Silo Enterprise Knowledge Fabric",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 8080, 
               log_level: str = "info", reload: bool = False):
    """Run the Synapse server"""
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload
    )


if __name__ == "__main__":
    run_server()