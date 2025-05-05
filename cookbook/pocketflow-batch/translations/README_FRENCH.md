<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/title.png" alt="Pocket Flow – 100-line minimalist LLM framework" width="600"/>
</div>

[English](https://github.com/The-Pocket/PocketFlow/blob/main/README.md) | [中文](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_CHINESE.md) | [Español](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_SPANISH.md) | [日本語](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_JAPANESE.md) | [Deutsch](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_GERMAN.md) | [Русский](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_RUSSIAN.md) | [Português](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_PORTUGUESE.md) | Français | [한국어](https://github.com/The-Pocket/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_KOREAN.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://the-pocket.github.io/PocketFlow/)
 <a href="https://discord.gg/hUHHE9Sa6T">
    <img src="https://img.shields.io/discord/1346833819172601907?logo=discord&style=flat">
</a>

Pocket Flow est un framework LLM minimaliste de [100 lignes](https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py)

- **Léger** : Seulement 100 lignes. Zéro superflu, zéro dépendance, zéro verrouillage fournisseur.
  
- **Expressif** : Tout ce que vous aimez — ([Multi-](https://the-pocket.github.io/PocketFlow/design_pattern/multi_agent.html))[Agents](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html), [Workflow](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html), [RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html), et plus encore.

- **[Codage Agentique](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to)** : Laissez les Agents IA (par exemple, Cursor AI) construire des Agents — productivité multipliée par 10 !

Commencer avec Pocket Flow :
- Pour installer, ```pip install pocketflow``` ou copiez simplement le [code source](https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py) (seulement 100 lignes).
- Pour en savoir plus, consultez la [documentation](https://the-pocket.github.io/PocketFlow/). Pour comprendre la motivation, lisez l'[histoire](https://zacharyhuang.substack.com/p/i-built-an-llm-framework-in-just).
- Des questions ? Consultez cet [Assistant IA](https://chatgpt.com/g/g-677464af36588191b9eba4901946557b-pocket-flow-assistant), ou [créez une issue !](https://github.com/The-Pocket/PocketFlow/issues/new)
- 🎉 Rejoignez notre [Discord](https://discord.gg/hUHHE9Sa6T) pour vous connecter avec d'autres développeurs utilisant Pocket Flow !
- 🎉 Pocket Flow est initialement en Python, mais nous avons maintenant des versions en [Typescript](https://github.com/The-Pocket/PocketFlow-Typescript), [Java](https://github.com/The-Pocket/PocketFlow-Java), [C++](https://github.com/The-Pocket/PocketFlow-CPP) et [Go](https://github.com/The-Pocket/PocketFlow-Go) !

## Pourquoi Pocket Flow ?

Les frameworks LLM actuels sont surchargés... Vous n'avez besoin que de 100 lignes pour un framework LLM !

<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/meme.jpg" width="400"/>


  |                | **Abstraction**          | **Wrappers spécifiques aux applications**                                      | **Wrappers spécifiques aux fournisseurs**                                    | **Lignes**       | **Taille**    |
|----------------|:-----------------------------: |:-----------------------------------------------------------:|:------------------------------------------------------------:|:---------------:|:----------------------------:|
| LangChain  | Agent, Chain               | Nombreux <br><sup><sub>(ex., QA, Résumé)</sub></sup>              | Nombreux <br><sup><sub>(ex., OpenAI, Pinecone, etc.)</sub></sup>                   | 405K          | +166MB                     |
| CrewAI     | Agent, Chain            | Nombreux <br><sup><sub>(ex., FileReadTool, SerperDevTool)</sub></sup>         | Nombreux <br><sup><sub>(ex., OpenAI, Anthropic, Pinecone, etc.)</sub></sup>        | 18K           | +173MB                     |
| SmolAgent   | Agent                      | Quelques <br><sup><sub>(ex., CodeAgent, VisitWebTool)</sub></sup>         | Quelques <br><sup><sub>(ex., DuckDuckGo, Hugging Face, etc.)</sub></sup>           | 8K            | +198MB                     |
| LangGraph   | Agent, Graph           | Quelques <br><sup><sub>(ex., Recherche Sémantique)</sub></sup>                     | Quelques <br><sup><sub>(ex., PostgresStore, SqliteSaver, etc.) </sub></sup>        | 37K           | +51MB                      |
| AutoGen    | Agent                | Quelques <br><sup><sub>(ex., Tool Agent, Chat Agent)</sub></sup>              | Nombreux <sup><sub>[Optionnel]<br> (ex., OpenAI, Pinecone, etc.)</sub></sup>        | 7K <br><sup><sub>(core uniquement)</sub></sup>    | +26MB <br><sup><sub>(core uniquement)</sub></sup>          |
| **PocketFlow** | **Graph**                    | **Aucun**                                                 | **Aucun**                                                  | **100**       | **+56KB**                  |

</div>

## Comment fonctionne Pocket Flow ?

Les [100 lignes](https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py) capturent l'abstraction fondamentale des frameworks LLM : le Graphe !
<br>
<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/abstraction.png" width="900"/>
</div>
<br>

À partir de là, il est facile d'implémenter des modèles de conception populaires comme ([Multi-](https://the-pocket.github.io/PocketFlow/design_pattern/multi_agent.html))[Agents](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html), [Workflow](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html), [RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html), etc.
<br>
<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/design.png" width="900"/>
</div>
<br>
✨ Voici des tutoriels de base :

<div align="center">
  
|  Nom  | Difficulté    |  Description  |  
| :-------------:  | :-------------: | :--------------------- |  
| [Chat](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-chat) | ☆☆☆ <br> *Facile*   | Un chatbot basique avec historique de conversation |
| [Sortie Structurée](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-structured-output) | ☆☆☆ <br> *Facile* | Extraction de données structurées à partir de CV par prompt |
| [Workflow](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-workflow) | ☆☆☆ <br> *Facile*   | Un workflow d'écriture qui établit le plan, rédige le contenu et applique le style |
| [Agent](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-agent) | ☆☆☆ <br> *Facile*   | Un agent de recherche qui peut chercher sur le web et répondre aux questions |
| [RAG](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-rag) | ☆☆☆ <br> *Facile*   | Un processus simple de génération augmentée par recherche |
| [Batch](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-batch) | ☆☆☆ <br> *Facile* | Un processeur par lots qui traduit du contenu markdown en plusieurs langues |
| [Streaming](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-llm-streaming) | ☆☆☆ <br> *Facile*   | Une démo de streaming LLM en temps réel avec possibilité d'interruption |
| [Chat Guardrail](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-chat-guardrail) | ☆☆☆ <br> *Facile*  | Un chatbot conseiller en voyage qui ne traite que les requêtes liées au voyage |
| [Map-Reduce](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-map-reduce) | ★☆☆ <br> *Débutant* | Un processeur de qualification de CV utilisant le modèle map-reduce pour l'évaluation par lots |
| [Multi-Agent](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-multi-agent) | ★☆☆ <br> *Débutant* | Un jeu de Tabou pour la communication asynchrone entre deux agents |
| [Superviseur](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-supervisor) | ★☆☆ <br> *Débutant* | L'agent de recherche devient peu fiable... Construisons un processus de supervision |
| [Parallèle](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-parallel-batch) | ★☆☆ <br> *Débutant*   | Une démo d'exécution parallèle montrant une accélération de 3x |
| [Flux Parallèle](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-parallel-batch-flow) | ★☆☆ <br> *Débutant*   | Une démo de traitement d'image en parallèle montrant une accélération de 8x avec plusieurs filtres |
| [Vote Majoritaire](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-majority-vote) | ★☆☆ <br> *Débutant* | Améliorer la précision du raisonnement en agrégeant plusieurs tentatives de solution |
| [Réflexion](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-thinking) | ★☆☆ <br> *Débutant*   | Résoudre des problèmes de raisonnement complexes grâce à la chaîne de pensée |
| [Mémoire](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-chat-memory) | ★☆☆ <br> *Débutant* | Un chatbot avec mémoire à court et long terme |
| [Text2SQL](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-text2sql) | ★☆☆ <br> *Débutant* | Convertir le langage naturel en requêtes SQL avec une boucle d'auto-débogage |
| [MCP](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-mcp) | ★☆☆ <br> *Débutant* | Agent utilisant le protocole MCP pour les opérations numériques |
| [A2A](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-a2a) | ★☆☆ <br> *Débutant* | Agent enveloppé avec le protocole Agent-to-Agent pour la communication inter-agents |
| [Web HITL](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook/pocketflow-web-hitl) | ★☆☆ <br> *Débutant* | Un service web minimal pour une boucle de révision humaine avec mises à jour SSE |

</div>

👀 Vous voulez voir d'autres tutoriels pour débutants ? [Créez une issue !](https://github.com/The-Pocket/PocketFlow/issues/new)

## Comment utiliser Pocket Flow ?

🚀 Via le **Codage Agentique** — le paradigme de développement d'applications LLM le plus rapide, où *les humains conçoivent* et *les agents codent* !

<br>
<div align="center">
  <a href="https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to" target="_blank">
    <img src="https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F423a39af-49e8-483b-bc5a-88cc764350c6_1050x588.png" width="700" alt="IMAGE ALT TEXT" style="cursor: pointer;">
  </a>
</div>
<br>

✨ Voici des exemples d'applications LLM plus complexes :

<div align="center">
  
|  Nom de l'application     |  Difficulté    | Sujets  | Conception Humaine | Code Agent |
| :-------------:  | :-------------: | :---------------------: |  :---: |  :---: |
| [Construire Cursor avec Cursor](https://github.com/The-Pocket/Tutorial-Cursor) <br> <sup><sub>Nous atteindrons bientôt la singularité ...</sup></sub> | ★★★ <br> *Avancé*   | [Agent](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html) | [Document de conception](https://github.com/The-Pocket/Tutorial-Cursor/blob/main/docs/design.md) | [Code Flow](https://github.com/The-Pocket/Tutorial-Cursor/blob/main/flow.py)
| [Constructeur de Connaissances de Code Base](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge) <br> <sup><sub>La vie est trop courte pour fixer le code des autres avec confusion</sup></sub> |  ★★☆ <br> *Moyen* | [Workflow](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html) | [Document de conception](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge/blob/main/docs/design.md) | [Code Flow](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge/blob/main/flow.py)
| [Demandez à l'IA Paul Graham](https://github.com/The-Pocket/Tutorial-YC-Partner) <br> <sup><sub>Demandez à l'IA Paul Graham, au cas où vous n'y accédiez pas</sup></sub> | ★★☆ <br> *Moyen*  | [RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html) <br> [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) <br> [TTS](https://the-pocket.github.io/PocketFlow/utility_function/text_to_speech.html) | [Document de conception](https://github.com/The-Pocket/Tutorial-AI-Paul-Graham/blob/main/docs/design.md) | [Code Flow](https://github.com/The-Pocket/Tutorial-AI-Paul-Graham/blob/main/flow.py)
| [Résumé Youtube](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple)  <br> <sup><sub> Explique les vidéos YouTube comme si vous aviez 5 ans </sup></sub> | ★☆☆ <br> *Débutant*   | [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) |  [Document de conception](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple/blob/main/docs/design.md) | [Code Flow](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple/blob/main/flow.py)
| [Générateur d'Accroches](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization)  <br> <sup><sub> Des brise-glaces instantanés qui transforment les prospects froids en chauds </sup></sub> | ★☆☆ <br> *Débutant*   | [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) <br> [Recherche Web](https://the-pocket.github.io/PocketFlow/utility_function/websearch.html) |  [Document de conception](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization/blob/master/docs/design.md) | [Code Flow](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization/blob/master/flow.py)

</div>

- Vous voulez apprendre le **Codage Agentique** ?

  - Consultez [ma chaîne YouTube](https://www.youtube.com/@ZacharyLLM?sub_confirmation=1) pour des tutoriels vidéo sur la façon dont certaines applications ci-dessus sont créées !

  - Vous voulez créer votre propre application LLM ? Lisez ce [post](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to) ! Commencez avec [ce modèle](https://github.com/The-Pocket/PocketFlow-Template-Python) !