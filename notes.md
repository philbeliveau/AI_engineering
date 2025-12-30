codex --sandbox danger-full-access --ask-for-approval never


  1. /bmad:bmm:workflows:create-prd - Create the PRD first                                               
  2. /bmad:bmm:workflows:create-epics-and-stories - Then create epics & stories (requires PRD +          
  Architecture)                                                                                          
  3. /bmad:bmm:workflows:check-implementation-readiness - Return here to validate everything             

  1. Sprint Planning - Use /bmad:bmm:workflows:sprint-planning to create    
  sprint tracking                                                           
  2. Story Creation - Use /bmad:bmm:workflows:create-story to expand        
  individual stories into implementation-ready specs                        
  3. Development - Use /bmad:bmm:workflows:dev-story to implement stories   
             
  1. Review the story: Check /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/impleme
  ntation-artifacts/1-1-initialize-monorepo-structure.md                                                 
  2. Optional Quality Check: Run /bmad:bmm:workflows:validate-create-story to have a fresh LLM           
  systematically review and improve the story context                                                    
  3. Implement: Run /bmad:bmm:workflows:dev-story for optimized implementation                           
  4. Code Review: Run /bmad:bmm:workflows:code-review when complete (auto-marks done)                    
