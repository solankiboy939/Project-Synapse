"""
Basic usage example for Project Synapse
"""

import asyncio
from synapse import (
    FederatedIndexer, PrivacyAwareQueryEngine, KnowledgeSynthesizer,
    DifferentialPrivacyManager, PermissionEngine
)
from synapse.models import (
    SiloMetadata, UserContext, QueryRequest, 
    AccessLevel, SiloType
)


async def main():
    """Demonstrate basic Synapse functionality"""
    
    print("🚀 Project Synapse - Basic Usage Example")
    print("=" * 50)
    
    # Initialize privacy manager
    privacy_manager = DifferentialPrivacyManager(global_privacy_budget=5.0)
    
    # Initialize core components
    federated_indexer = FederatedIndexer(privacy_manager=privacy_manager)
    query_engine = PrivacyAwareQueryEngine(federated_indexer)
    synthesizer = KnowledgeSynthesizer()
    
    # Create example silos
    silos = [
        SiloMetadata(
            silo_id="eng_docs",
            name="Engineering Documentation",
            silo_type=SiloType.DOCUMENTATION,
            organization_id="acme_corp",
            team_id="engineering",
            access_rules={"public_within_org": True},
            data_classification=AccessLevel.INTERNAL
        ),
        SiloMetadata(
            silo_id="code_repo",
            name="Main Code Repository", 
            silo_type=SiloType.CODE_REPOSITORY,
            organization_id="acme_corp",
            team_id="engineering",
            access_rules={"allowed_teams": ["engineering"]},
            data_classification=AccessLevel.CONFIDENTIAL
        ),
        SiloMetadata(
            silo_id="support_kb",
            name="Support Knowledge Base",
            silo_type=SiloType.KNOWLEDGE_BASE,
            organization_id="acme_corp", 
            team_id="support",
            access_rules={"public_within_org": True},
            data_classification=AccessLevel.INTERNAL
        )
    ]
    
    print(f"📊 Indexing {len(silos)} silos...")
    
    # Build federated index
    global_index = await federated_indexer.build_global_index(silos)
    
    print(f"✅ Indexing completed!")
    print(f"   - Indexed silos: {global_index['indexed_silos']}")
    print(f"   - Privacy budget used: {global_index['privacy_budget_used']:.4f}")
    
    # Create user context
    user_context = UserContext(
        user_id="john.doe",
        organization_id="acme_corp",
        team_ids=["engineering", "devops"],
        access_levels=[AccessLevel.INTERNAL, AccessLevel.CONFIDENTIAL]
    )
    
    # Execute federated query
    print(f"\n🔍 Executing federated query...")
    
    query_request = QueryRequest(
        query="How to implement authentication in microservices?",
        user_context=user_context,
        max_results=5,
        privacy_budget=0.2
    )
    
    results = await query_engine.route_query(query_request)
    
    print(f"📋 Query Results ({len(results)} found):")
    print("-" * 40)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.source_attribution['silo']}")
        print(f"   Relevance: {result.relevance_score:.3f}")
        print(f"   Content: {result.content[:100]}...")
        print(f"   Access Level: {result.access_level}")
        print()
    
    # Synthesize knowledge
    if results:
        print("🧠 Synthesizing knowledge...")
        
        synthesis = await synthesizer.synthesize_answers(
            query_request.query,
            results,
            user_context
        )
        
        print("📝 Knowledge Synthesis:")
        print("-" * 40)
        print(synthesis.synthesized_answer)
        print(f"\nConfidence Score: {synthesis.confidence_score:.2f}")
        print(f"Sources Used: {len(synthesis.source_results)}")
        
        if synthesis.limitations:
            print("\n⚠️  Limitations:")
            for limitation in synthesis.limitations:
                print(f"   - {limitation}")
    
    # Privacy report
    print(f"\n🔒 Privacy Report:")
    privacy_report = privacy_manager.get_privacy_report()
    print(f"   - Remaining budget: {privacy_report['remaining_budget']:.4f}")
    print(f"   - Usage: {privacy_report['usage_percentage']:.1f}%")
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())