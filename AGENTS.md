The goal of this repo is to leverage the bmad builder: _bmad/bmb
So that we can encode books, methodology and good AI engineering practices to build agentic solution. 

The idea is that these books, ressources, are actually expert playbook that we can encode their methodology and use bmad AI agent workflow to solve and build complex agentic application. 
The philosophy: Instead of reading a 1000 page book and trying to generalize it on your own set of problems, we use agentic workflow to map the framework, the structure we need to approach these problems. Every agent in the workflow could represent a step, for example, we could have a first agent that is focus on the business application, which would structure the thinking process of defining the problem within the solution space, i.e the enterprise operation, business goals, stakeholders involve. To really challenge the user on the adequacy of building an agentic application, to help the user define the MVP given the constraint (i.e the team description, the time to market, etc)
Then, build a second agent focused on the data, what's available, what is the current enterprise architecture, etc. 
Then a third agent, loading the establish context and generated specifictation from step 1 and 2 (i.e business agent and data agent), that will discuss about the possible stack to use, why it fits the use case (i.e, qdrant, zenML, sagemaker or GCP, Azure)
Then, an agent that helps making sure and deciphering the feature pipeline, the training pipeline, the inference pipeline
Then, an agent helping designing evaluation metrics, given the context of the problems, loadings all previous architecture choice. 
...

All these agents would act not as solving the problems for the user, but as making the user good through the right steps to build an efficient AI engineering applications, at every step, the agent can have up to date knowledge base about best practices, pre-define workflows that make them reads specific docs, make operation, challenge the architecture, generate recommendation. 

Information is not expertise, expert is methodology, knowing what questions to ask and when. 
These frameworks are use to reduce the cognitive load of applying these 1000 page books, they are made to simplify the work of the user, to learn by doing. 

For more context about these bmad workflow, you can read: _bmad, and https://github.com/bmad-code-org/BMAD-METHOD
