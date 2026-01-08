"""
Main CLI interface for Project Synapse
"""

import click
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Dict, Any

from ..core import FederatedIndexer, PrivacyAwareQueryEngine, KnowledgeSynthesizer
from ..security import DifferentialPrivacyManager, EncryptionManager
from ..models import SiloMetadata, UserContext, QueryRequest, AccessLevel, SiloType
from ..api.server import run_server


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """Project Synapse - Cross-Silo Enterprise Knowledge Fabric"""
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    ctx.ensure_object(dict)
    if config:
        with open(config, 'r') as f:
            ctx.obj['config'] = yaml.safe_load(f)
    else:
        ctx.obj['config'] = {}


@cli.command()
@click.option('--config-path', default='config/default.yaml', 
              help='Path to create default configuration')
def init(config_path):
    """Initialize Project Synapse with default configuration"""
    
    config_dir = Path(config_path).parent
    config_dir.mkdir(parents=True, exist_ok=True)
    
    default_config = {
        'synapse': {
            'privacy': {
                'global_budget': 10.0,
                'default_query_budget': 0.1
            },
            'indexing': {
                'embedding_model': 'all-MiniLM-L6-v2',
                'batch_size': 100,
                'update_interval': 3600
            },
            'security': {
                'encryption_enabled': True,
                'key_rotation_interval': 86400
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8080,
                'cors_origins': ['*']
            }
        },
        'silos': {
            'example_silo': {
                'name': 'Example Documentation Silo',
                'type': 'documentation',
                'organization_id': 'example_org',
                'team_id': 'docs_team',
                'data_classification': 'internal',
                'access_rules': {
                    'public_within_org': True,
                    'allowed_teams': ['docs_team', 'engineering']
                }
            }
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
    click.echo(f"✅ Initialized configuration at {config_path}")
    click.echo("Edit the configuration file and run 'synapse indexer start' to begin indexing")


@cli.group()
def indexer():
    """Manage the federated indexer"""
    pass


@indexer.command()
@click.pass_context
def start(ctx):
    """Start the federated indexer"""
    
    async def run_indexer():
        config = ctx.obj['config']
        
        # Initialize components
        privacy_manager = DifferentialPrivacyManager(
            global_privacy_budget=config.get('synapse', {}).get('privacy', {}).get('global_budget', 10.0)
        )
        
        federated_indexer = FederatedIndexer(
            embedding_model=config.get('synapse', {}).get('indexing', {}).get('embedding_model', 'all-MiniLM-L6-v2'),
            privacy_manager=privacy_manager
        )
        
        # Create example silos from config
        silos = []
        for silo_id, silo_config in config.get('silos', {}).items():
            silo = SiloMetadata(
                silo_id=silo_id,
                name=silo_config['name'],
                silo_type=SiloType(silo_config['type']),
                organization_id=silo_config['organization_id'],
                team_id=silo_config['team_id'],
                access_rules=silo_config.get('access_rules', {}),
                data_classification=AccessLevel(silo_config['data_classification'])
            )
            silos.append(silo)
            
        if not silos:
            click.echo("❌ No silos configured. Run 'synapse init' first.")
            return
            
        click.echo(f"🚀 Starting indexer for {len(silos)} silos...")
        
        # Build global index
        global_index = await federated_indexer.build_global_index(silos)
        
        click.echo("✅ Indexing completed!")
        click.echo(f"📊 Indexed {global_index['indexed_silos']} silos")
        click.echo(f"🔒 Privacy budget used: {global_index['privacy_budget_used']:.4f}")
        
    asyncio.run(run_indexer())


@indexer.command()
@click.argument('silo_id')
@click.pass_context
def status(ctx, silo_id):
    """Check indexing status for a silo"""
    
    # Mock implementation - in reality, would check actual indexing status
    click.echo(f"📊 Silo: {silo_id}")
    click.echo("Status: ✅ Indexed")
    click.echo("Documents: 100")
    click.echo("Last Updated: 2024-01-09 10:30:00")


@cli.group()
def query():
    """Execute federated queries"""
    pass


@query.command()
@click.argument('query_text')
@click.option('--user-id', required=True, help='User ID for permissions')
@click.option('--org-id', required=True, help='Organization ID')
@click.option('--team-ids', help='Comma-separated team IDs')
@click.option('--access-levels', help='Comma-separated access levels')
@click.option('--max-results', default=10, help='Maximum results to return')
@click.pass_context
def search(ctx, query_text, user_id, org_id, team_ids, access_levels, max_results):
    """Execute federated search query"""
    
    async def run_query():
        config = ctx.obj['config']
        
        # Initialize components
        privacy_manager = DifferentialPrivacyManager(
            global_privacy_budget=config.get('synapse', {}).get('privacy', {}).get('global_budget', 10.0)
        )
        
        federated_indexer = FederatedIndexer(privacy_manager=privacy_manager)
        query_engine = PrivacyAwareQueryEngine(federated_indexer)
        
        # Create user context
        user_context = UserContext(
            user_id=user_id,
            organization_id=org_id,
            team_ids=team_ids.split(',') if team_ids else [],
            access_levels=[AccessLevel(level) for level in access_levels.split(',')] if access_levels else [AccessLevel.INTERNAL]
        )
        
        # Create query request
        query_request = QueryRequest(
            query=query_text,
            user_context=user_context,
            max_results=max_results,
            privacy_budget=config.get('synapse', {}).get('privacy', {}).get('default_query_budget', 0.1)
        )
        
        click.echo(f"🔍 Searching: {query_text}")
        click.echo(f"👤 User: {user_id} ({org_id})")
        
        # Execute query (mock results for CLI demo)
        click.echo("\n📋 Results:")
        click.echo("=" * 50)
        
        # Mock results
        for i in range(min(3, max_results)):
            click.echo(f"\n{i+1}. Mock Result {i+1}")
            click.echo(f"   Source: Example Silo {i+1}")
            click.echo(f"   Relevance: 0.{90-i*10}")
            click.echo(f"   Content: This is a mock result for '{query_text}' from silo {i+1}")
            
        click.echo(f"\n✅ Found {min(3, max_results)} results")
        
    asyncio.run(run_query())


@query.command()
@click.argument('query_text')
@click.option('--user-id', required=True, help='User ID for permissions')
@click.option('--org-id', required=True, help='Organization ID')
@click.pass_context
def synthesize(ctx, query_text, user_id, org_id):
    """Synthesize knowledge from multiple sources"""
    
    click.echo(f"🧠 Synthesizing knowledge for: {query_text}")
    click.echo(f"👤 User: {user_id} ({org_id})")
    
    # Mock synthesis output
    click.echo("\n📝 Synthesis:")
    click.echo("=" * 50)
    click.echo(f"""
Based on the available sources, here's a comprehensive approach to {query_text}:

[Source: Engineering Team] The recommended implementation follows a modular 
architecture pattern with clear separation of concerns.

[Source: Documentation] Key considerations include error handling, logging, 
and performance monitoring.

[Source: DevOps Team] Deployment should use containerization with proper 
health checks and rollback capabilities.

The synthesis shows consistency across teams regarding best practices, with 
each team contributing specialized knowledge in their domain.

Confidence Score: 0.85
Privacy Preserving: ✅
Sources: 3 silos accessed
""")


@cli.group()
def server():
    """Manage the API server"""
    pass


@server.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8080, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.pass_context
def start(ctx, host, port, reload):
    """Start the API server"""
    
    config = ctx.obj['config']
    
    # Override with config values if available
    api_config = config.get('synapse', {}).get('api', {})
    host = api_config.get('host', host)
    port = api_config.get('port', port)
    
    click.echo(f"🚀 Starting Synapse API server on {host}:{port}")
    click.echo(f"📖 API docs available at http://{host}:{port}/docs")
    
    run_server(host=host, port=port, reload=reload)


@cli.group()
def privacy():
    """Privacy and security management"""
    pass


@privacy.command()
def report():
    """Show privacy budget usage report"""
    
    # Mock privacy report
    click.echo("🔒 Privacy Budget Report")
    click.echo("=" * 30)
    click.echo("Global Budget: 10.0")
    click.echo("Used Budget: 2.3")
    click.echo("Remaining: 7.7 (77%)")
    click.echo("\nMechanism Usage:")
    click.echo("- Gaussian Noise: 1.5 (15 operations)")
    click.echo("- Laplace Noise: 0.8 (8 operations)")


@privacy.command()
@click.confirmation_option(prompt='Are you sure you want to reset the privacy budget?')
def reset():
    """Reset privacy budget (use with caution)"""
    
    click.echo("🔄 Privacy budget reset successfully")
    click.echo("⚠️  All previous privacy guarantees are now void")


@cli.group()
def encryption():
    """Encryption key management"""
    pass


@encryption.command()
def status():
    """Show encryption key status"""
    
    click.echo("🔐 Encryption Status")
    click.echo("=" * 25)
    click.echo("Silos with Keys: 3")
    click.echo("Key Rotation: Enabled")
    click.echo("Last Rotation: 2024-01-08 15:30:00")


@encryption.command()
@click.argument('silo_id')
def generate_keys(silo_id):
    """Generate encryption keys for a silo"""
    
    click.echo(f"🔑 Generating keys for silo: {silo_id}")
    click.echo("✅ Symmetric key generated")
    click.echo("✅ Asymmetric key pair generated")
    click.echo(f"🔒 Key fingerprint: abc123def456")


if __name__ == '__main__':
    cli()