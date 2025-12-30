# FTI

1. Feature pipeline
2. Training pipeline 
3. Inference pipeline 

# Stack 
HuggingFace	Model registry
Comet ML	Experiment tracker
Opik	Prompt monitoring
ZenML	Orchestrator and artifacts layer
AWS	Compute and storage
MongoDB	NoSQL database
Qdrant	Vector database
Poetry 
ODM - ORM 

# Data structure 
« The NoSQL data warehouse documents
    We had to implement three document classes to structure our data categories. These classes define the specific attributes we require for a document, such as the content, author, and source link. It is best practice to structure your data in classes instead of dictionaries, as the attributes we expect for each item are more verbose, reducing run errors. For example, when accessing a value from a Python dictionary, we can never be sure it is present or its type is current. By wrapping our data items with classes, we can ensure each attribute is as expected. »

## ORM
« Before we talk about software patterns, let’s see what ORM is. It’s a technique that lets you query and manipulate data from a database using an object-oriented paradigm. Instead of writing SQL or API-specific queries, you encapsulate all the complexity under an ORM class that knows how to handle all the database operations, most commonly CRUD operations. Thus, working with ORM removes the need to handle the database operations manually and reduces the need to write boilerplate code manually. An ORM interacts with a SQL database, such as PostgreSQL or MySQL.

Most modern Python applications use ORMs when interacting with the database. Even though SQL is still a popular choice in the data world, you rarely see raw SQL queries in Python backend components. The most popular Python ORM is SQLAlchemy (https://www.sqlalchemy.org/). Also, with the rise of FastAPI, SQLModel is (https://github.com/fastapi/sqlmodel) a common choice, which is a wrapper over SQLAlchemy that makes the integration easier with FastAPI.
For example, using SQLAlchemy, we defined a User ORM with the ID and name fields. The User ORM is mapped to the users table within the SQL database. Thus, when we create a new user and[…] »

# Chapter 4 RAG 231:
« An overview of advanced RAG
    The vanilla RAG framework we just presented doesn’t address many fundamental aspects that impact the quality of the retrieval and answer generation, such as:
    
      Are the retrieved documents relevant to the user’s question?
      Is the retrieved context enough to answer the user’s question?
      Is there any redundant information that only adds noise to the augmented prompt?
      Does the latency of the retrieval step match our requirements?
      What do we do if we can’t generate a valid answer using the retrieved information?
    
    From the questions above, we can draw two conclusions. The first one is that we need a robust evaluation module for our RAG system that can quantify and measure the quality of the retrieved data and generate answers relative to the user’s question. We will discuss this topic in more detail in Chapter 9. The second conclusion is that we must improve our RAG framework to address the retrieval limitations directly in the algorithm. These improvements are known as advanced RAG.
    The vanilla RAG design can be optimized at three different stages:
    
      Pre-retrieval: This stage focuses on how to structure and preprocess your data for data indexing optimizations as well as query optimizations[…] » 

« The vanilla RAG design can be optimized at three different stages:
    
      Pre-retrieval: This stage focuses on how to structure and preprocess your data for data indexing optimizations as well as query optimizations.
      Retrieval: This stage revolves around improving the embedding models and metadata filtering to improve the vector search step.
      Post-retrieval: This stage mainly targets different ways to filter out noise from the retrieved documents and compress the prompt before feeding it to an LLM for answer generation. »
Pre-retrieval
The pre-retrieval steps are performed in two different ways:
Data indexing: It is part of the RAG ingestion pipeline. It is mainly
implemented within the cleaning or chunking modules to
preprocess the data for better indexing.
Query optimization: The algorithm is performed directly on the
user’s query before embedding it and retrieving the chunks from
the vector DB.
As we index our data using embeddings that semantically represent
the content of a chunked document, most of the data indexing
techniques focus on better preprocessing and structuring the data to
improve retrieval efficiency, such as:
Sliding window: The sliding window technique introduces overlap
between text chunks, ensuring that important context near chunk
boundaries is retained, which enhances retrieval accuracy. This is
particularly beneficial in domains like legal documents, scientific
papers, customer support logs, and medical records, where
critical information often spans multiple sections. The embedding
is computed on the chunk along with the overlapping portion.
Hence, the sliding window improves the system’s ability to retrieve
relevant and coherent information by maintaining context across
boundaries.
Enhancing data granularity: This involves data cleaning
techniques like removing irrelevant details, verifying factual
accuracy, and updating outdated information. A clean and
accurate dataset allows for sharper retrieval.
Metadata: Adding metadata tags like dates, URLs, external IDs,
or chapter markers helps filter results efficiently during retrieval.
Optimizing index structures: It is based on different data index
methods, such as various chunk sizes and multi-indexing
strategies.
Small-to-big: The algorithm decouples the chunks used for
retrieval and the context used in the prompt for the final answer
generation. The algorithm uses a small sequence of text to
compute the embedding while preserving the sequence itself and
a wider window around it in the metadata. Thus, using smaller
chunks enhances the retrieval’s accuracy, while the larger context
adds more contextual information to the LLM.
The intuition behind this is that if we use the whole text for computing
the embedding, we might introduce too much noise, or the text could
contain multiple topics, which results in a poor overall semantic
representation of the embedding

On the query optimization side, we can leverage techniques such
as query routing, query rewriting, and query expansion to refine the
retrieved information for the LLM further:
Query routing: Based on the user’s input, we might have to
interact with different categories of data and query each category
differently. Query rooting is used to decide what action to take
based on the user’s input, similar to if/else statements. Still, the
decisions are made solely using natural language instead of
logical statements.
As illustrated in Figure 4.6, let’s assume that, based on the user’s
input, to do RAG, we can retrieve additional context from a vector
DB using vector search queries, a standard SQL DB by translating
the user query to an SQL command, or the internet by leveraging
REST API calls. The query router can also detect whether a context
is required, helping us avoid making redundant calls to external data
storage. Also, a query router can be used to pick the best prompt
template for a given input. For example, in the LLM Twin use case,
depending on whether the user wants an article paragraph, a post,
or a code snippet, you need different prompt templates to optimize
the creation process. The routing usually uses an LLM to decide
what route to take or embeddings by picking the path with the most
similar vectors. To summarize, query routing is identical to an if/else
statement but much more versatile as it works directly with natural
language.
Query rewriting: Sometimes, the user’s initial query might not
perfectly align with the way your data is structured. Query
rewriting tackles this by reformulating the question to match the
indexed information better. This can involve techniques like:
Paraphrasing: Rephrasing the user’s query while preserving
its meaning (e.g., “What are the causes of climate change?”
could be rewritten as “Factors contributing to global warming”).
Synonym substitution: Replacing less common words with
synonyms to broaden the search scope (e.g., “ joyful” could be
rewritten as “happy”).
Sub-queries: For longer queries, we can break them down into
multiple shorter and more focused sub-queries. This can help
the retrieval stage identify relevant documents more precisely.
Hypothetical document embeddings (HyDE): This technique
involves having an LLM create a hypothetical response to the
query. Then, both the original query and the LLM’s response are
fed into the retrieval stage.
Query expansion: This approach aims to enrich the user’s
question by adding additional terms or concepts, resulting in
different perspectives of the same initial question. For example,
when searching for “disease,” you can leverage synonyms and
related terms associated with the original query words and also
include “illnesses” or “ailments.”
Self-query: The core idea is to map unstructured queries into
structured ones. An LLM identifies key entities, events, and
relationships within the input text. These identities are used as
filtering parameters to reduce the vector search space (e.g.,
identify cities within the query, for example, “Paris,” and add it to
your filter to reduce your vector search space).
Both data indexing and query optimization pre-retrieval optimization
techniques depend highly on your data type, structure, and source.
Thus, as with any data processing pipeline, no method always
works, as every use case has its own particularities and gotchas.
Optimizing your pre-retrieval RAG layer is experimental. Thus, what
is essential is to try multiple methods (such as the ones enumerated
in this section), reiterate, and observe what works best.
Retrieval
The retrieval step can be optimized in two fundamental ways:
Improving the embedding models used in the RAG ingestion
pipeline to encode the chunked documents and, at inference time,
transform the user’s input.
Leveraging the DB’s filter and search features. This step will
be used solely at inference time when you have to retrieve the
most similar chunks based on user input.
Both strategies are aligned with our ultimate goal: to enhance the
vector search step by leveraging the semantic similarity between the
query and the indexed data.
When improving the embedding models, you usually have to fine-
tune the pre-trained embedding models to tailor them to specific
jargon and nuances of your domain, especially for areas with
evolving terminology or rare terms.
Instead of fine-tuning the embedding model, you can leverage
instructor models
(https://huggingface.co/hkunlp/instructor-xl) to guide the
embedding generation process with an instruction/prompt aimed at
your domain. Tailoring your embedding network to your data using
such a model can be a good option, as fine-tuning a model
consumes more computing and human resources.
In the code snippet below, you can see an example of an Instructor
model that embeds article titles about AI:
from InstructorEmbedding import INSTRUCTOR model = INSTRUCTOR("hkunlp/instructor-base") sentence = "RAG Fundamentals First" instruction = "Represent the title of an article a
embeddings = model.encode([[instruction, sentence]