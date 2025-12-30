  Decisions                                                                                                
                                                                                                           
  What: Choice points where an engineer must pick between options.                                         
                                                                                                           
  Example from an AI engineering book:                                                                     
                                                                                                           
  {                                                                                                        
    "question": "Which embedding model should I use for RAG?",                                             
    "options": ["OpenAI text-embedding-3", "Cohere embed-v3", "Local sentence-transformers"],              
    "considerations": "Cost vs quality vs latency vs privacy. OpenAI has best quality but ongoing costs.   
  Local models are free but lower quality. Cohere is middle ground.",                                      
    "recommendation": "Start with sentence-transformers for prototyping, switch to OpenAI for production if
   budget allows"                                                                                          
  }                                                                                                        
                                                                                                           
  Why extract: When a user asks "how do I choose an embedding model?", we return this structured decision  
  framework, not just paragraphs of text.                                                                  
                                                                                                           
  ---                                                                                                      
  Patterns                                                                                                 
                                                                                                           
  What: Reusable code structures or architectural approaches.                                              
                                                                                                           
  Example:                                                                                                 
                                                                                                           
  {                                                                                                        
    "name": "RAG Pipeline with Reranking",                                                                 
    "description": "Two-stage retrieval: fast vector search then precise reranking",                       
    "code": "results = vector_store.search(query, k=100)\nreranked = reranker.rerank(query, results,       
  top_k=10)",                                                                                              
    "language": "python",                                                                                  
    "use_case": "When you need high precision retrieval and can afford extra latency"                      
  }                                                                                                        
                                                                                                           
  Why extract: When building a workflow step, we can suggest actual implementation patterns, not just      
  concepts.                                                                                                
                                                                                                           
  ---                                                                                                      
  Warnings                                                                                                 
                                                                                                           
  What: Gotchas, anti-patterns, and "don't do this" advice.                                                
                                                                                                           
  Example:                                                                                                 
                                                                                                           
  {                                                                                                        
    "issue": "Using semantic chunking on tabular data",                                                    
    "consequence": "Tables get split mid-row, destroying data relationships and retrieval accuracy",       
    "mitigation": "Detect tables during parsing, keep them as atomic chunks or convert to structured format
   first"                                                                                                  
  }                                                                                                        
                                                                                                           
  Why extract: Proactive guidance. When a user is building a RAG system with PDFs that contain tables, we  
  surface this warning automatically.                                                                      
                                                                                                           
  ---                                                                                                      
  How They Work Together                                                                                   
                                                                                                           
  When someone uses the AI Engineering framework and asks:                                                 
                                                                                                           
  "I'm building a RAG system for technical documentation with lots of tables"                              
                                                                                                           
  The MCP search returns:                                                                                  
  - Decisions: Chunking strategy options, embedding model choices                                          
  - Patterns: Table-aware parsing code, hybrid search implementation                                       
  - Warnings: The table chunking gotcha above                                                              
                                                                                                           
  Instead of generic text, they get actionable, structured guidance.                   


  # The real architecture

    ---                                                                                                       
  The Real Architecture                                                                                     
                                                                                                            
  Pre-extractions = Structured Index for Exploration                                                        
  Raw chunks = Source material for Synthesis                                                                
  Claude = Judge that synthesizes across sources                                                            
                                                                                                            
  ┌─────────────────────────────────────────────────────────────────────┐                                   
  │                        KNOWLEDGE BASE                                │                                  
  │                                                                      │                                  
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │                                    
  │  │ LLM Handbook │  │ LLMs in Prod │  │ Research     │  ...more     │                                    
  │  │              │  │              │  │ Papers       │              │                                    
  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │                                    
  │         │                 │                 │                       │                                   
  │         ▼                 ▼                 ▼                       │                                   
  │  ┌─────────────────────────────────────────────────────────────┐   │                                    
  │  │  EXTRACTIONS (Structured Index)                              │   │                                   
  │  │  - 47 decisions from Handbook                                │   │                                   
  │  │  - 32 decisions from LLMs in Prod                           │   │                                    
  │  │  - 15 decisions from papers                                  │   │                                   
  │  │  → Searchable, filterable, explorable                       │   │                                    
  │  └─────────────────────────────────────────────────────────────┘   │                                    
  │                              +                                       │                                  
  │  ┌─────────────────────────────────────────────────────────────┐   │                                    
  │  │  RAW CHUNKS (Full Context)                                   │   │                                   
  │  │  - All original text, preserved                              │   │                                   
  │  │  → For deep reading, synthesis, context                     │   │                                    
  │  └─────────────────────────────────────────────────────────────┘   │                                    
  └─────────────────────────────────────────────────────────────────────┘                                   
                                │                                                                           
                                │ Query                                                                     
                                ▼                                                                           
  ┌─────────────────────────────────────────────────────────────────────┐                                   
  │  CLAUDE (Judge + Synthesizer)                                        │                                  
  │                                                                      │                                  
  │  Receives:                                                          │                                   
  │  - Relevant extractions from multiple sources                       │                                   
  │  - Raw chunks for context                                           │                                   
  │  - User's specific situation                                        │                                   
  │                                                                      │                                  
  │  Does:                                                               │                                  
  │  - Compares perspectives across sources                             │                                   
  │  - Weighs conflicting recommendations                               │                                   
  │  - Synthesizes based on user's context                              │                                   
  │  - Goes BEYOND what any single source says                          │                                   
  │  - Cites sources for traceability                                   │                                   
  └─────────────────────────────────────────────────────────────────────┘                                   
                                                                                                            
  ---                                                                                                       
  Query Flow Example                                                                                        
                                                                                                            
  User: "What chunking strategy should I use for RAG with technical documentation?"                         
                                                                                                            
  Step 1: Retrieve Extractions (Structured)                                                                 
  Decisions found across sources:                                                                           
  - LLM Handbook: "Fixed vs semantic chunking" (recommends: semantic)                                       
  - LLMs in Prod: "Chunk size selection" (recommends: 512 tokens)                                           
  - Paper 2024: "Hierarchical chunking" (recommends: parent-child)                                          
  - Case Study: "Table-aware chunking" (recommends: detect tables first)                                    
                                                                                                            
  Step 2: Retrieve Raw Chunks (Context)                                                                     
  Full paragraphs explaining each approach, with nuance and caveats                                         
                                                                                                            
  Step 3: Claude Synthesizes                                                                                
  "Based on 4 sources, here are your options:                                                               
                                                                                                            
  1. Semantic chunking (LLM Handbook's default recommendation)                                              
  2. Hierarchical/parent-child (newer research, better for complex docs)                                    
  3. Table-aware preprocessing (critical for technical docs)                                                
                                                                                                            
  Given you mentioned technical documentation, I'd combine approaches:                                      
  - Detect and isolate tables first (Case Study insight)                                                    
  - Use hierarchical chunking for prose (Paper recommendation)                                              
  - Target ~512 tokens per leaf chunk (LLMs in Prod)                                                        
                                                                                                            
  This goes beyond any single source's recommendation because                                               
  your use case spans multiple concerns."                                                                   
                                                                                                            
  ---                                                                                                       
  What Extractions Enable                                                                                   
                                                                                                            
  | Capability                   | How Extractions Help                                                |    
  |------------------------------|---------------------------------------------------------------------|    
  | "What do we know about X?"   | Query extractions by topic, get structured overview                 |    
  | "Compare sources on X"       | Retrieve decisions from multiple sources, show agreements/conflicts |    
  | "What options exist for X?"  | Aggregate options across all Decision extractions                   |    
  | "Show me all warnings for X" | Filter extractions by type=warning, topic=X                         |    
  | "What's covered vs not?"     | Gap analysis: topics with extractions vs topics with none           |    
                                                                                                            
  ---                                                                                                       
  What Claude's Judgment Enables                                                                            
                                                                                                            
  | Capability          | How Claude Adds Value                                                |            
  |---------------------|----------------------------------------------------------------------|            
  | Conflict resolution | Book A says X, Book B says Y → Claude weighs based on user context   |            
  | Gap filling         | No extraction covers this edge case → Claude reasons from principles |            
  | Context application | User has specific constraints → Claude filters/prioritizes           |            
  | Synthesis           | Combine pattern from A + warning from B + decision from C            |            
  | Going beyond        | "Based on these sources AND my training, I'd also consider..."       |            
                                                                                                            
  ---                                                                                                       
  Revised Storage Model                                                                                     
                                                                                                            
  MongoDB                                                                                                   
  ├── sources                                                                                               
  │   ├── {id: "llm-handbook", type: "book", ...}                                                           
  │   ├── {id: "llms-in-prod", type: "book", ...}                                                           
  │   └── {id: "rag-survey-2024", type: "paper", ...}                                                       
  │                                                                                                         
  ├── chunks                                                                                                
  │   └── {id, source_id, content, position, ...}  # Raw text                                               
  │                                                                                                         
  └── extractions                                                                                           
      └── {                                                                                                 
            id,                                                                                             
            source_id,                                                                                      
            chunk_id,                                                                                       
            type: "decision" | "pattern" | "warning",                                                       
            content: { ... structured ... },                                                                
            topics: ["rag", "chunking"],                                                                    
            ...                                                                                             
          }                                                                                                 
                                                                                                            
  Qdrant                                                                                                    
  ├── chunk_vectors      # For "find relevant context"                                                      
  └── extraction_vectors # For "find relevant decisions/patterns/warnings"                                  
                                                                                                            
  ---                                                                                                       
  MCP Tools Revised                                                                                         
                                                                                                            
  @mcp_tool                                                                                                 
  async def explore_knowledge(                                                                              
      topic: str,                                                                                           
      extraction_types: List[str] = ["decision", "pattern", "warning"],                                     
      sources: List[str] = None  # Filter by source, or all                                                 
  ) -> ExplorationResult:                                                                                   
      """                                                                                                   
      Structured exploration: What do we know about X?                                                      
      Returns extractions from all matching sources.                                                        
      """                                                                                                   
                                                                                                            
  @mcp_tool                                                                                                 
  async def search_context(                                                                                 
      query: str,                                                                                           
      include_extractions: bool = True,                                                                     
      include_chunks: bool = True,                                                                          
      limit: int = 10                                                                                       
  ) -> SearchResult:                                                                                        
      """                                                                                                   
      Semantic search for synthesis.                                                                        
      Returns both extractions AND raw chunks.                                                              
      Claude uses this to synthesize answers.                                                               
      """                                                                                                   
                                                                                                            
  @mcp_tool                                                                                                 
  async def compare_sources(                                                                                
      topic: str,                                                                                           
      extraction_type: str = "decision"                                                                     
  ) -> ComparisonResult:                                                                                    
      """                                                                                                   
      What do different sources say about X?                                                                
      Returns grouped extractions for Claude to judge.                                                      
      """                                                                                                   
                                                                                                            
  ---                                                                                                       
  The Key Insight                                                                                           
                                                                                                            
  Extractions are for NAVIGATION, not ANSWERS.                                                              
                                                                                                            
  - They tell you what knowledge exists and where                                                           
  - They structure the exploration space                                                                    
  - They enable comparison across sources                                                                   
                                                                                                            
  Claude is for SYNTHESIS and JUDGMENT.                                                                     
                                                                                                            
  - It reads the extractions + raw context                                                                  
  - It weighs, compares, resolves conflicts                                                                 
  - It applies to user's specific situation                                                                 
  - It goes beyond any single source                                                                        
                                                     