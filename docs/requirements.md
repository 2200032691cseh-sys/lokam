# LOKAM — A WORLD OF YOUR OWN

## Engineering mandate

Lokam is designed as a maintainable, secure and accessible web application.

Think from first principles. Choose technologies according to actual requirements rather than popularity. Minimize infrastructure, dependencies, operational complexity and recurring expenditure.

The developer is a single person using a Windows computer with limited computational resources and no initial infrastructure budget.

Do not implement the entire application immediately.

First establish the complete product specification, architecture, database design, frontend design system, security model, external integrations, deployment strategy, testing strategy and dependency-ordered implementation backlog.

Wait for explicit architecture approval before feature implementation.

Do not silently remove, simplify or postpone product requirements. Distinguish genuine engineering constraints from unnecessary complexity.

---

# 1. Product definition

**Product name:** Lokam

**Tagline:** A world of your own.

Lokam is a personal interests, entertainment discovery, cultural exploration and self-expression platform.

Every user receives a personal website representing everything they find interesting.

The platform learns from explicitly saved interests and recommends relevant entertainment, knowledge, destinations and experiences across domains.

The product must provide substantial value even when there is only one registered user.

Social functionality supplements the personal experience rather than being a prerequisite for it.

## Problems being solved

1. Personal interests are fragmented across unrelated applications.
2. Entertainment recommendation systems generally operate within individual media categories.
3. Interesting discoveries are frequently forgotten.
4. Connections between literature, cinema, music, history, culture and travel are difficult to discover systematically.
5. People lack a unified representation of their personal tastes and interests.
6. Creating and maintaining a personal website requires technical knowledge or significant manual effort.
7. Conventional social platforms prioritize popularity and engagement rather than meaningful interests.

## Core product loop

Discover → Explore → Collect → Understand preferences → Discover more.

Users should collect things because they genuinely enjoy them, not because they are required to populate a profile.

Saving an item should improve future discovery.

The personal website should emerge naturally from the user's collections.

---

# 2. Non-negotiable product principles

- Curiosity over productivity.
- Enjoyment over achievement.
- Connection over popularity.
- Exploration over completion.
- Self-expression over performance.
- User ownership of personal information.
- Privacy by design.
- No compulsory ratings or reviews.
- No mandatory personal activity dates.
- No reading, watching or listening streaks.
- No reading or viewing progress tracking.
- No productivity scores.
- No intelligence or personality scores.
- No public popularity metrics.
- No follower-count competition.
- No infinite scrolling.
- No engagement-maximizing algorithms.
- No compulsory publishing.
- No empty-profile shaming.
- No unnecessary artificial intelligence.
- No unnecessary manual data entry.

The platform must never imply that someone is inferior because of their interests, collection size, knowledge or activity.

---

# 3. User roles

## Anonymous visitor

- Browse publicly accessible profiles.
- Explore public collections.
- Search public catalogue information.
- View public item details.
- Explore public relationships between subjects.
- Register or log in.

## Registered user

- Maintain a personal website.
- Manage personal interests.
- Discover recommendations.
- Create collections.
- Save favourites.
- Manage memories.
- Follow other users.
- Control privacy.
- Import and export personal information.
- Delete their account.

## Moderator

- Review assigned reports.
- Investigate content violations.
- Apply authorized moderation actions.
- Maintain moderation records.

## Administrator

- Manage platform operations.
- Manage catalogue integrity.
- Configure external integrations.
- Manage authorized moderation and administrative functions.
- Monitor infrastructure and security.

Administrative access must be restricted and audited.

---

# 4. Personal website structure

Every user receives a website under:

`/u/<username>/`

The personal website contains exactly 20 primary pages.

1. Home
2. Books
3. Movies
4. TV Shows
5. Music
6. History
7. Culture & Heritage
8. Travel
9. Food & Cuisine
10. Languages
11. Mythology & Folklore
12. Philosophy & Psychology
13. Activities & Experiences
14. Learning & Exploration
15. Photography & Memories
16. Collections
17. Favourites
18. Lifetime Bucket List
19. Statistics
20. Personal Timeline

Users may hide, enable and reorder personal pages.

Empty pages must not create pressure to populate them.

---

# 5. Complete personal page requirements

## 5.1 Home

A traditional personal website introducing the person and their interests.

Support:

- Optional personal introduction.
- Optional profile photograph.
- Links to enabled interest pages.
- Selected favourites.
- Featured collections.
- Selected memories.
- Selected bucket list entries.
- Cross-domain interest connections.
- Follow and unfollow controls for visitors.
- Optional shared-interest information.

Profile introductions are user-authored and optional.

Do not add an introductory title, subtitle or tagline to personal introductions.

Do not display recent activity, currently reading, currently watching or productivity dashboards.

## 5.2 Books

Support:

- All books.
- Read.
- Want to read.
- Set aside.
- Favourites.
- Authors.
- Genres.
- Themes.
- Characters.
- Series.
- Editions.
- Collections.
- Literary preferences.
- Optional personal thoughts.
- Optional ratings.
- Favourite passages.
- Favourite characters.
- Personal significance.
- Ownership information.
- Cover images.
- Publication metadata.
- Languages.
- ISBNs.
- Adaptations.
- Related historical subjects.
- Related cultural subjects.
- Related destinations.
- Related books.
- Cross-domain recommendations.

Personal reading dates and reading progress are excluded.

## 5.3 Movies

Support:

- All movies.
- Watched.
- Want to watch.
- Favourites.
- Cast.
- Directors.
- Writers.
- Genres.
- Themes.
- Languages.
- Countries.
- Characters.
- Franchises.
- Adaptations.
- Posters.
- Release metadata.
- Optional personal thoughts.
- Optional ratings.
- Favourite scenes.
- Favourite performances.
- Favourite dialogue.
- Soundtracks.
- Related historical events.
- Related cultural subjects.
- Related destinations.
- Cross-domain recommendations.

Do not host copyrighted movies.

## 5.4 TV Shows

Support:

- All shows.
- Watched.
- Want to watch.
- Favourites.
- Creators.
- Cast.
- Characters.
- Genres.
- Themes.
- Languages.
- Countries.
- Seasons and episodes as reference metadata.
- Favourite seasons and episodes.
- Favourite characters.
- Favourite relationships.
- Optional personal thoughts.
- Optional ratings.
- Posters.
- Adaptations.
- Related movies.
- Related books.
- Related music.
- Historical and cultural relationships.
- Cross-domain recommendations.

Do not implement episode completion tracking.

## 5.5 Music

Support:

- Artists.
- Composers.
- Songs.
- Recordings.
- Albums.
- Musical works.
- Genres.
- Languages.
- Instruments.
- Musical traditions.
- Moods.
- Favourite music.
- Personal playlists and collections.
- Album artwork.
- Artist photographs.
- Optional personal associations and memories.
- Film and television soundtrack relationships.
- Cultural and historical relationships.
- Links to legitimate listening services.
- Music discovery.

Do not host copyrighted audio or implement listening-time tracking.

## 5.6 History

Support:

- Historical periods.
- Civilizations.
- Kingdoms.
- Empires.
- Historical figures.
- Dynasties.
- Events.
- Political movements.
- Historical places.
- Archaeological sites.
- Historical questions.
- Personal notes.
- Favourite historical subjects.
- Related books.
- Related films.
- Related television shows.
- Related documentaries.
- Related museums and destinations.
- Historical discovery.

Lokam is a personal exploration system, not a replacement for historical reference sources.

## 5.7 Culture & Heritage

Support:

- Cultures.
- Regions.
- Communities.
- Traditions.
- Customs.
- Festivals.
- Heritage sites.
- Cultural expressions.
- Literature.
- Music.
- Cinema.
- Craftsmanship.
- Personal cultural heritage.
- Cultural experiences.
- Related languages.
- Related cuisines.
- Related mythology.
- Related history.
- Cultural discovery.

Avoid cultural superiority rankings and unsupported cultural generalizations.

## 5.8 Travel

Support:

- Countries.
- Regions.
- Cities.
- Towns.
- Landmarks.
- Museums.
- Historical sites.
- Archaeological sites.
- Natural destinations.
- Visited places.
- Places of interest.
- Places the user wants to visit.
- Favourites.
- Personal travel collections.
- Optional memories.
- Photographs.
- Geographic map.
- Related historical subjects.
- Related literature.
- Related films.
- Related cuisines.
- Related cultures.
- Destination discovery.

Do not implement travel competitions, completion percentages or compulsory travel dates.

## 5.9 Food & Cuisine

Support:

- Dishes.
- Cuisines.
- Ingredients.
- Flavours.
- Textures.
- Favourite foods.
- Foods of interest.
- Saved recipes.
- Favourite restaurants.
- Personal food experiences.
- Regional culinary traditions.
- Related cultures.
- Related destinations.
- Food discovery.

Do not implement nutrition scoring, calorie tracking or weight management.

## 5.10 Languages

Support:

- Languages known.
- Languages of interest.
- Writing systems.
- Scripts.
- Alphabets.
- Favourite words.
- Favourite phrases.
- Linguistic subjects.
- Dictionaries.
- Learning resources.
- Related literature.
- Related music.
- Related cinema.
- Related cultures.
- Language discovery.

No compulsory proficiency assessments or learning streaks.

## 5.11 Mythology & Folklore

Support:

- Mythological traditions.
- Folkloric traditions.
- Myths.
- Legends.
- Folktales.
- Mythological figures.
- Creatures.
- Associated places.
- Related cultures.
- Related literature.
- Related movies.
- Related television.
- Related historical subjects.
- Personal notes.
- Discovery.

Clearly distinguish mythology, religious traditions, folklore and documented history.

## 5.12 Philosophy & Psychology

Support:

- Philosophical concepts.
- Psychological concepts.
- Thinkers.
- Philosophers.
- Psychologists.
- Philosophical schools.
- Intellectual traditions.
- Questions of interest.
- Books.
- Lectures.
- Articles.
- Personal reflections.
- Related literature.
- Related history.
- Related films.
- Concept discovery.

Do not infer psychological diagnoses or personality assessments.

## 5.13 Activities & Experiences

Support:

- Hobbies.
- Recreational activities.
- Creative activities.
- Outdoor experiences.
- Cultural experiences.
- Meaningful everyday experiences.
- Favourite activities.
- Activities of interest.
- Personal memories.
- Related destinations.
- Related learning resources.
- Experience discovery.

No performance scoring or mandatory dates.

## 5.14 Learning & Exploration

Support:

- Subjects.
- Concepts.
- Courses.
- Lectures.
- Educational videos.
- Podcasts.
- Articles.
- Websites.
- Books.
- Questions.
- Saved learning resources.
- Personal notes.
- Favourite resources.
- Related interests.
- Discovery.

No deadlines, grades, study-time tracking or productivity features.

## 5.15 Photography & Memories

Support:

- Personal photographs.
- Albums.
- Captions.
- Stories.
- Childhood memories.
- Meaningful experiences.
- Travel memories.
- Relationships with saved interests.
- Optional dates.
- Manual organization.
- Private albums.
- Image descriptions.
- Downloading.
- Editing.
- Deletion.

Strip sensitive EXIF information from publicly served images.

## 5.16 Collections

Users can create collections spanning any number of interest domains.

Support:

- Custom titles.
- Descriptions.
- Cover images.
- Manual ordering.
- Adding and removing items.
- Cross-domain items.
- Visibility controls.
- Sharing.
- Saving references to public collections.
- Related collection discovery.

Example collection: Renaissance Florence, containing books, television shows, historical figures, cultural subjects and travel destinations.

## 5.17 Favourites

Provide a unified view of explicitly favourited content across all domains.

Support filtering, organization, selected home-page favourites and recommendation generation.

No mandatory rankings.

## 5.18 Lifetime Bucket List

Support:

- Places.
- Books.
- Films.
- Shows.
- Experiences.
- Hobbies.
- Cultural activities.
- Languages.
- Learning interests.
- Custom aspirations.
- Optional experienced or fulfilled state.
- Manual ordering.
- Privacy controls.

No deadlines, countdowns or completion percentages.

## 5.19 Statistics

Provide descriptive insights into saved interests.

Support:

- Genre distributions.
- Favourite themes.
- Historical periods of interest.
- Cultural interests.
- Geographic interests.
- Language interests.
- Preferred creators.
- Recurring subjects.
- Cross-domain connections.
- Distribution of saved interests.

Explain how each insight was derived.

Do not infer intelligence, personality, productivity, social status or personal worth.

## 5.20 Personal Timeline

A manually curated representation of life chapters and interests.

Support:

- Childhood interests.
- Meaningful discoveries.
- Personal chapters.
- Experiences.
- Memories.
- Rediscovered interests.
- Manually ordered chapters.
- Optional dates.
- Relationships with saved items.

Do not generate an automatic chronological activity history.

---

# 6. Platform-level pages

Implement:

- Landing page.
- Discover.
- Global search.
- Catalogue item details.
- Sign up.
- Log in.
- Log out.
- Email verification.
- Password recovery.
- Onboarding.
- Followers.
- Following.
- Follow requests.
- Saved items.
- Notifications.
- Account settings.
- Profile settings.
- Privacy settings.
- Blocked accounts.
- Import.
- Export.
- Help.
- About Lokam.
- Privacy policy.
- Terms of service.
- Community guidelines.
- Data and image credits.
- Content reporting.
- Moderation interface.
- Administrative interface.

---

# 7. Onboarding and content acquisition

Minimize time to first useful recommendation.

Require only essential account information.

Allow users to:

- Select interests.
- Search for favourite items.
- Add items with one confirmation.
- Skip optional fields.
- Skip profile customization.
- Receive recommendations after saving a small number of items.
- Import existing collections.
- Add custom items manually.

Support bulk text entry, CSV and JSON imports.

Implement supported Goodreads and Letterboxd export-file importers where their actual formats permit.

Do not scrape authenticated third-party accounts or bypass platform restrictions.

## Add-item workflow

1. Search the shared local catalogue.
2. If necessary, search permitted external providers.
3. Display matching items with images and distinguishing metadata.
4. Let the user select the correct item.
5. Normalize and persist permitted catalogue information.
6. Create the user's personal relationship with that item.
7. Update relevant recommendations.
8. Make the item available on the appropriate personal page.

A user must not have to manually type metadata that already exists.

---

# 8. Unified entertainment and discovery engine

This is a primary product feature, not an optional enhancement.

The recommendation engine must understand explicitly expressed interests across all domains.

Books should influence movie recommendations.

Movies should influence music, literature, history and travel recommendations.

Historical interests should influence entertainment and cultural recommendations.

The system must function without other users or collaborative filtering.

## 8.1 Discovery categories

Implement:

- Books.
- Movies.
- TV shows.
- Music.
- Documentaries.
- Educational videos.
- Podcasts.
- Historical subjects.
- Cultures.
- Destinations.
- Cuisine.
- Languages.
- Mythology.
- Philosophical concepts.
- Psychological concepts.
- Activities.
- Experiences.
- Learning resources.
- Public collections.
- Related people.
- Unexpected discoveries.

Documentaries belong to movie or television subtypes as appropriate.

Podcasts, lectures and educational videos belong to Learning & Exploration.

Do not create additional primary personal pages.

## 8.2 Preference representation

Represent interests using:

- Explicit favourites.
- Explicitly saved items.
- Optional ratings.
- Explicitly selected themes.
- Genres.
- Creators.
- Characters.
- Historical periods.
- Geographic locations.
- Cultures.
- Languages.
- Musical styles.
- Narrative themes.
- Settings.
- Subject relationships.
- Explicit recommendation feedback.

Do not treat a saved item as definitive proof that a user likes every attribute associated with it.

Favourites provide stronger preference evidence than items saved for possible future exploration.

Use explicit feedback rather than covert behavioural profiling.

## 8.3 Knowledge graph

Represent factual relationships between catalogue entities.

Supported relationships include:

- Adapted from.
- Adaptation of.
- Written by.
- Directed by.
- Created by.
- Composed by.
- Performed by.
- Features character.
- Depicts historical figure.
- Depicts historical event.
- Set in location.
- Set during period.
- Associated with culture.
- Associated with language.
- Soundtrack of.
- Part of series.
- Part of franchise.
- Associated with mythology.
- Influenced by.
- Located in.
- Associated with cuisine.
- Shares subject.
- Shares theme.

Store graph edges in PostgreSQL.

Each factual relationship must include provenance.

Distinguish:

1. Verified factual relationships.
2. Provider-supplied recommendations.
3. Computed similarities.
4. User-created personal connections.

Never represent semantic similarity as an established historical or factual relationship.

## 8.4 Cross-provider entity resolution

Normalize identities using:

- Wikidata QIDs.
- Open Library work and edition identifiers.
- ISBNs.
- TMDB identifiers.
- MusicBrainz identifiers.
- Other permitted stable external identifiers.

Prefer exact external identifiers.

Use normalized titles, creators, dates and entity types only as secondary matching evidence.

Do not automatically merge ambiguous records.

Provide administrative duplicate review and merge functionality.

Preserve references during merges.

## 8.5 Recommendation candidate generation

Generate candidates using multiple independent methods.

### Factual relationships

Traverse relevant knowledge graph edges.

Example:

Historical novel → historical figure → related film → associated destination.

### Content-based filtering

Find items sharing meaningful metadata with saved interests.

### Provider recommendations

Use permitted recommendations supplied by domain-specific providers.

### Semantic similarity

Use text embeddings to compare meaningful descriptions, themes and subjects across domains.

### Creator and entity relationships

Find related works involving shared creators, characters, historical figures or other entities.

### Serendipity

Include controlled exploration beyond established interests.

### Collaborative filtering

Do not require collaborative filtering.

Introduce it only if sufficient users and interaction data exist, its privacy implications are acceptable, and measured evaluation demonstrates meaningful improvements.

## 8.6 Recommendation ranking

Develop an explainable ranking pipeline.

Candidate scoring may incorporate:

- Explicit preference relevance.
- Factual relationship strength.
- Shared themes.
- Semantic similarity.
- Shared creators.
- Shared historical or cultural subjects.
- Provider recommendation evidence.
- Novelty.
- Diversity.
- Explicit negative feedback.

Normalize scoring components before combining them.

Treat ranking weights as configurable engineering parameters, not proven measures of human taste.

Evaluate and tune weights using representative test cases.

Do not optimize for time spent, clicks, compulsive usage or advertising revenue.

## 8.7 Recommendation presentation

Every recommendation should explain why it appears.

Examples:

- Based on your interest in Tudor England.
- Shares themes with your favourite historical novels.
- Adapted from a book in your collection.
- Features an artist you enjoy.
- Connected to a historical figure you saved.
- Explores a culture you find interesting.

Use factual explanations only where supported by evidence.

Use appropriately qualified language for computed similarities.

## 8.8 Discover page

Provide:

- Recommendations based on all saved interests.
- Domain-specific recommendations.
- Cross-domain recommendations.
- Related subjects.
- Thematic exploration.
- Geographic exploration.
- Historical exploration.
- Cultural exploration.
- Entertainment discovery.
- Rediscovery of saved interests.
- Unexpected discoveries.
- User-controlled filters.

Allow users to select the type of content they want to discover.

Allow users to dismiss recommendations and indicate that they are not interested.

Allow users to reset recommendation preferences.

Do not require an infinite feed.

## 8.9 Cold-start behaviour

For users without saved items:

- Offer optional interest selection.
- Offer catalogue exploration.
- Provide curated starting subjects.
- Allow direct search.
- Explain that saving favourites improves recommendations.

Do not pretend to know a user's preferences without evidence.

## 8.10 Recommendation evaluation

Maintain a representative evaluation dataset covering:

- Within-domain recommendations.
- Cross-domain recommendations.
- Ambiguous entities.
- Sparse profiles.
- Diverse profiles.
- Conflicting preferences.
- Incorrect factual relationships.
- Duplicate recommendations.
- Missing metadata.
- Unavailable external providers.
- Privacy boundaries.

Evaluate relevance, diversity, factual correctness, explanation correctness, catalogue coverage and computational cost.

Do not claim recommendation quality without testing.

---

# 9. External data integrations

Use free or appropriately licensed data sources wherever possible.

## Books

Open Library:

- Work and edition metadata.
- Authors.
- ISBNs.
- Subjects.
- Cover references.
- Related literary subjects.

## Movies and television

Wikidata provides credential-free film and television metadata.

- Film and television metadata.
- Cast and creators.
- Genres.
- Keywords.
- Posters.
- Seasons and episodes.
- Similar titles.
- Provider recommendations.

Use reviewed sources for fields that Wikidata does not cover. Track provider suggestions separately from computed similarities.

## Music

MusicBrainz:

- Artists.
- Releases.
- Release groups.
- Recordings.
- Musical works.
- Artist relationships.

Cover Art Archive:

- Album cover references.

Verify image rights and commercial API terms.

## Cross-domain knowledge

Wikidata:

- Entity identifiers.
- Historical subjects.
- Geographic entities.
- Cultures.
- Languages.
- Creators.
- Adaptations.
- Subject relationships.
- Other supported structured relationships.

Use Wikidata as the principal external cross-domain relationship source.

## Supporting sources

- Wikipedia for permitted summaries and reference links.
- Wikimedia Commons for appropriately licensed images.
- Wikivoyage for permitted travel information.
- Wiktionary for permitted linguistic information.
- OpenStreetMap for geographic data.
- RSS and Atom feeds for supported public resources.

Do not assume that these providers offer comprehensive coverage for every domain.

Provide manual entry and source-link fallbacks.

## Integration architecture

Create independent provider adapters.

Each adapter must handle:

- Authentication where required.
- Request timeouts.
- Rate limits.
- Retry policies.
- Response validation.
- Normalization.
- Provenance.
- Licensing.
- Attribution.
- Caching restrictions.
- Provider failures.
- Schema changes.

Do not perform unrestricted web scraping.

Do not download entire external datasets without evaluating storage and processing requirements.

Use targeted retrieval and permitted incremental imports.

Never expose API credentials to the browser.

---

# 10. Conversational profile feature

Design an optional conversational interface for exploring a user's explicitly shared interests.

This is a separate optional capability. The core platform must function completely without an LLM.

The conversational assistant may answer questions about:

- Saved interests.
- Favourite books.
- Favourite movies.
- Musical preferences.
- Historical interests.
- Collections.
- Shared interests.
- Potential conversation topics.
- Related discoveries.

The assistant must identify itself as an AI interface to profile information.

It must not impersonate the profile owner.

It must not invent personal opinions, memories, experiences, preferences or intentions.

## Architecture

Use retrieval-augmented generation.

1. Authenticate the requesting user where necessary.
2. Verify that the profile owner enabled conversational access.
3. Determine which records the requester is authorized to access.
4. Retrieve relevant authorized information.
5. Construct bounded model context.
6. Generate a grounded answer.
7. Provide links to supporting records.
8. Refuse to invent missing information.

Support revocation of conversational access.

Protect against prompt injection, unauthorized retrieval and cross-user data leakage.

Do not allow the LLM to execute database queries directly or perform arbitrary application actions.

## Local development

Evaluate Ollama or llama.cpp with a suitable small open-weight language model.

Select the actual model after benchmarking quality, RAM consumption, CPU latency and licensing.

Do not assume that local CPU inference can serve a public production workload.

## Production

Use a provider-independent model interface.

Enable the feature only when a reliable, affordable and privacy-compatible inference deployment exists.

Do not introduce a mandatory paid AI dependency.

---

# 11. Social architecture

Implement:

- Follow.
- Unfollow.
- Private-profile follow requests.
- Approve and reject requests.
- Followers and following lists.
- Mutual following.
- Public profile discovery.
- Shared public interests.
- Saving public catalogue references.
- Saving public collections.
- Profile sharing.
- Collection sharing.
- Blocking.
- Reporting.
- Essential notifications.

Do not implement:

- Public follower counts.
- Like counts.
- Trending profiles.
- Popularity rankings.
- Engagement-driven feeds.
- Public attractiveness or intelligence scores.
- Dating functionality.
- AI-generated social messages.
- Direct messaging or public comments without separate product approval.

Blocking and privacy rules must apply consistently across all social surfaces.

---

# 12. Frontend design system

## Design reference

https://karpathy.ai/

Use the simplicity of a traditional personal website.

Do not copy the reference website's source code or identity.

The design must not resemble a SaaS dashboard, productivity application, corporate portal or conventional social media feed.

## Colour palette

- Main background: #080F24
- Secondary background: #101B35
- Optional content surface: #172440
- Borders and separators: #293A59
- Primary text: #E8EDF7
- Secondary text: #A3B1CD
- Links: #9BAED5

Use the colours of a dark, cozy, midnight-blue atmosphere.

Do not introduce stars, planets, celestial imagery or space-themed decoration.

## Typography

Use a system sans-serif font stack.

Initial typography tokens:

- Body: 16px.
- Body line height: approximately 1.6.
- Main heading: approximately 28px.
- Section heading: approximately 21px.
- Subheading: approximately 18px.
- Secondary text: approximately 14px.

Validate contrast, readability and responsive scaling.

## Layout

- Centred document-style content.
- Approximately 850px default reading width.
- Wider layouts where catalogue content requires them.
- Simple text navigation.
- Natural scrolling.
- Thin separators.
- Restrained rectangular controls.
- Meaningful images.
- Comfortable spacing.
- Responsive list and grid layouts.
- Pagination.
- Consistent forms.

Avoid unnecessary cards, shadows, gradients, animations, decorative badges, glassmorphism, bento layouts, giant hero sections and dashboard sidebars.

## Personal home page

The introduction appears naturally as ordinary text.

Below it, display enabled personal page links.

Optional featured content follows.

Do not add marketing slogans to personal profiles.

## Catalogue pages

Support:

- Page title.
- Simple navigation.
- Search.
- Relevant filters.
- List view.
- Grid view where appropriate.
- Item images.
- Item titles.
- Essential metadata.
- Personal relationship controls.
- Pagination.
- Empty states.
- Error states.
- Loading states where necessary.

## Discover page

Use a simple editorial layout organized by meaningful recommendation groups.

Display recommendation explanations alongside results.

Avoid endless recommendation feeds.

## Accessibility

Target WCAG 2.2 AA.

Implement:

- Semantic HTML.
- Keyboard navigation.
- Visible focus indicators.
- Screen-reader-compatible forms.
- Accessible validation messages.
- Appropriate alternative text.
- Sufficient contrast.
- Reduced-motion support.
- Responsive text.
- Accessible dialogs.
- Logical heading order.
- Skip navigation.
- Accessible status announcements.

Use native HTML controls wherever practical.

Core operations must work without JavaScript whenever technically reasonable.

---

# 13. Technology stack

## Core application

- Python.
- Django 5.2 LTS, subject to supported-version verification.
- Django Templates.
- Django Forms.
- Django ORM.
- HTML5.
- Plain CSS.
- Vanilla JavaScript.
- PostgreSQL.
- Psycopg 3.
- Django Auth.
- Argon2 password hashing.
- Database-backed sessions.
- HTTPX for external HTTP integrations.
- Pillow for image processing.
- uv for Python dependency management.
- Git and GitHub.

Use supported, mutually compatible versions and commit dependency lockfiles.

## Search

- PostgreSQL full-text search.
- PostgreSQL pg_trgm.
- Indexed normalized identifiers.
- Language-aware search where supported.
- Appropriate fallback search for multilingual metadata.

## Recommendation engine

- Python.
- PostgreSQL relational queries.
- PostgreSQL knowledge graph tables.
- NumPy where numerical operations justify it.
- pgvector for semantic retrieval.
- Sentence Transformers or an equivalent lightweight embedding runtime.

Evaluate a compact multilingual embedding model, such as multilingual-e5-small, against the actual catalogue.

Benchmark model quality and computational requirements before final selection.

Do not require a GPU.

Precompute catalogue embeddings outside interactive web requests.

Do not embed the same canonical item separately for every user.

## Maps

- Leaflet.
- Appropriately licensed geographic data and map tiles.

Verify tile-provider policies and capacity.

Provide a non-map destination list fallback.

## Media

- Pillow.
- Django storage abstraction.
- django-storages where required.
- S3-compatible object storage.
- Local filesystem storage for development.

## Production serving

- Gunicorn for conventional WSGI application serving.
- WhiteNoise for versioned static assets.
- HTTPS.
- Environment-managed configuration.

If conversational streaming is enabled, evaluate an appropriate ASGI deployment using Uvicorn rather than forcing long-lived streaming through unsuitable synchronous workers.

## Testing

- Pytest.
- pytest-django.
- Factory Boy.
- Hypothesis for important invariant testing.
- Playwright.
- axe-core.
- Coverage.py.
- Locust for measured load testing.

## Engineering quality

- Ruff.
- mypy and django-stubs where useful.
- pip-audit.
- Targeted security scanning.
- GitHub Actions.
- Pre-commit hooks.

Avoid redundant tools that provide no measurable engineering benefit.

---

# 14. System architecture

Use a modular monolith.

One primary Django application.

One primary PostgreSQL database.

One object storage abstraction.

One shared catalogue.

Independent personal records belonging to individual users.

A bounded background processing system.

Optional model inference infrastructure.

## Request flow

Browser → HTTPS endpoint → Django middleware → Authentication → Authorization → View/form → Domain service → ORM → PostgreSQL → Server-rendered HTML.

## External metadata flow

Provider adapter → Response validation → Normalization → Entity resolution → Provenance storage → Shared catalogue.

## Recommendation flow

Authorized personal interests → Preference representation → Candidate generation → Ranking → Diversity and deduplication → Explanation generation → Recommendation results.

## Media flow

Upload → Validation → Safe decoding → Metadata removal → Image transformation → Object storage → Authorized delivery.

## Architectural boundaries

Separate modules according to genuine domain responsibilities.

Do not introduce microservices.

Do not create internal HTTP calls between modules.

Do not implement unnecessary generic repository layers over Django ORM.

Use explicit service functions for complex business operations.

Use transactions for multi-record state changes.

Keep external integrations separate from core domain logic.

Avoid hidden business logic in signals.

Use dependency direction that prevents circular imports.

---

# 15. Database architecture

The central distinction is between shared catalogue information and user-owned personal information.

A book, film, album or historical figure should have a canonical identity.

Each user maintains an independent relationship with that entity.

## Identity and profile models

- User.
- Profile.
- ProfilePage.
- ProfileSettings.
- PrivacySettings.
- EmailVerification.

Create the custom Django user model before the initial migration.

## Catalogue models

- CatalogueItem.
- ExternalIdentifier.
- CatalogueSource.
- CatalogueImage.
- CatalogueAlias.
- CatalogueRelationship.
- Person.
- ItemPersonRole.
- Genre.
- Theme.
- Tag.
- ItemTag.

## Domain models

- Book.
- BookEdition.
- Movie.
- TVShow.
- TVSeason.
- TVEpisode.
- MusicArtist.
- MusicAlbum.
- MusicRecording.
- HistoricalEntity.
- Culture.
- Place.
- Cuisine.
- Dish.
- Language.
- MythologicalEntity.
- Concept.
- Activity.
- LearningResource.

Use shared catalogue identity and explicit domain-specific fields.

Do not duplicate information unnecessarily.

## Personal models

- UserItem.
- UserNote.
- UserPreference.
- UserItemTag.
- UserItemRelationship.
- UserQuote.
- Collection.
- CollectionItem.
- BucketListItem.
- Memory.
- Album.
- AlbumMedia.
- TimelineChapter.
- TimelineItem.
- Bookmark.

Represent favourites as an attribute of a user's relationship where appropriate.

## Discovery models

- CatalogueEmbedding.
- RecommendationFeedback.
- RecommendationSnapshot or cache, if justified.
- RecommendationExplanation or structured evidence.
- ExplicitPreference.
- DiscoveryConfiguration.

Do not persist every generated recommendation indefinitely.

Avoid unnecessary duplication between preference models.

Refine the final schema during architecture review.

## Social models

- Follow.
- FollowRequest.
- Block.
- Notification.
- Report.
- ModerationAction.

Evaluate whether follow requests and accepted relationships can share a single stateful model without compromising clarity.

## Operational models

- MediaAsset.
- ImportJob.
- ExportJob.
- BackgroundJob.
- AuditEvent.
- ProviderSyncState.

## Database requirements

- Foreign keys.
- Unique constraints.
- Check constraints.
- Explicit deletion behaviour.
- Appropriate indexes.
- Transactional integrity.
- Idempotent operations.
- Safe migrations.
- Provenance tracking.
- Efficient pagination.
- Query-count verification.
- No unbounded database queries.

Use JSONB only for genuinely flexible supplementary information.

Do not use JSONB as a substitute for relational integrity.

Technical timestamps are permitted for maintenance and security. They must not become personal activity-tracking features.

---

# 16. Search architecture

Implement:

- Exact title matching.
- Partial matching.
- Typo tolerance.
- Alternative names.
- Creator search.
- Genre and theme search.
- Domain filters.
- Personal library search.
- Public profile search.
- Collection search.
- Cross-domain subject search.
- External catalogue fallback.

Evaluate multilingual search for English, Telugu and other Unicode content.

Do not require AI for ordinary search.

Use semantic retrieval only where it measurably improves discovery.

Search results, snippets, counts, autocomplete and related-item suggestions must enforce privacy.

---

# 17. Background processing

Implement bounded asynchronous work for:

- Bulk imports.
- Data exports.
- Permitted metadata enrichment.
- Embedding generation.
- Image processing.
- Email delivery.
- Recommendation refreshes.
- Duplicate review.
- Maintenance.
- Backup coordination.

Initially evaluate a PostgreSQL-backed durable job mechanism.

Do not build a complex distributed task framework.

If implementing a database-backed worker, require:

- Atomic job claiming.
- Idempotency.
- Retry limits.
- Backoff.
- Execution timeouts.
- Crash recovery.
- Failure inspection.
- Authorization.
- Cancellation where appropriate.
- Resource limits.

Avoid expensive work inside interactive HTTP requests.

If zero-budget infrastructure cannot reliably support a continuous worker, document the limitation and use supported bounded or scheduled alternatives.

Do not silently assume free continuous background processing exists.

---

# 18. Privacy and authorization

Visibility levels:

- Public.
- Approved followers.
- Private.

Apply visibility to:

- Profiles.
- Personal pages.
- User items.
- Notes.
- Collections.
- Memories.
- Albums.
- Timeline chapters.
- Bucket list entries.
- Statistics.
- Conversational profile access.

Use the most restrictive applicable permission when content appears through multiple relationships.

A public collection must not expose a private item.

A public recommendation explanation must not reveal private preference evidence.

A blocked user must not bypass restrictions through search, media URLs, recommendations, exports or conversational interfaces.

Enforce authorization server-side.

Create centralized, testable access policies.

Use private storage for private media.

Provide explicit user controls for publication and sharing.

Do not make sensitive personal information public by default.

---

# 19. Security requirements

Implement protection against:

- CSRF.
- XSS.
- SQL injection.
- Broken object-level authorization.
- Session theft.
- Credential stuffing.
- Brute-force authentication.
- Account enumeration.
- SSRF.
- Malicious file uploads.
- Image decompression bombs.
- Malicious imports.
- Spam.
- Impersonation.
- Harassment.
- Unauthorized data export.
- Dependency vulnerabilities.
- Secret leakage.
- Prompt injection.
- Cross-user AI context leakage.

Use:

- Argon2 password hashing.
- Secure cookies.
- HttpOnly cookies.
- Appropriate SameSite policies.
- HTTPS.
- HSTS in production.
- Content Security Policy.
- Security headers.
- Rate limiting.
- Email verification.
- Restricted external HTTP access.
- File-size and image-dimension limits.
- Safe image re-encoding.
- Template escaping.
- Validated inputs.
- Least-privilege database credentials.
- Administrator MFA.
- Audited administrative actions.

Do not accept arbitrary remote image URLs without a safe retrieval policy.

Do not expose sensitive information in logs.

Provide account recovery and session invalidation.

---

# 20. Media and copyright

Support automatic image retrieval from permitted sources.

Examples:

- Open Library book covers.
- Appropriately licensed movie and television images.
- Cover Art Archive album covers.
- Wikimedia Commons photographs and illustrations.

Store image source, attribution and licensing metadata.

Do not assume API access grants redistribution rights.

Respect provider-specific image delivery requirements.

Support:

- Missing-image placeholders.
- Optional custom images.
- Responsive image sizes.
- Lazy loading.
- Image descriptions.
- Storage quotas.
- Deletion.
- Orphaned-media cleanup.
- Private media access.

Do not host copyrighted films, television episodes, books or music.

Use legitimate external links.

Limit user-submitted quotations according to applicable copyright requirements.

Implement copyright reporting and removal procedures.

---

# 21. Import, export and account deletion

Support:

- CSV imports.
- JSON imports.
- Supported third-party export formats.
- Bulk text entry.
- Duplicate detection.
- Import preview.
- Import validation.
- Error reports.
- Safe retries.

Users must be able to export their own information in documented machine-readable formats.

Include personal records, relationships, collections, preferences and permitted media references.

Do not export third-party content beyond applicable rights.

Implement account deletion with documented handling of:

- Personal information.
- Private media.
- Social relationships.
- Notifications.
- Background jobs.
- Recommendation caches.
- Conversational data.
- Shared catalogue records.
- Backup retention.
- Legally required records.

Deleting an account must not delete shared canonical items used by other users.

---

# 22. Repository architecture

Use the following logical structure as a starting point.

    lokam/
        manage.py
        pyproject.toml
        uv.lock
        README.md
        .env.example
        .gitignore

        config/
            settings/
                base.py
                development.py
                production.py
                test.py
            urls.py
            wsgi.py
            asgi.py

        apps/
            core/
            accounts/
            profiles/
            catalogue/
            libraries/
            collections/
            memories/
            timeline/
            discovery/
            search/
            social/
            media/
            moderation/
            integrations/
            jobs/
            portability/
            operations/

        templates/
            platform/
            profiles/
            catalogue/
            libraries/
            discovery/
            components/
            accounts/
            settings/
            errors/
            emails/

        static/
            css/
            js/
            images/
            vendor/

        tests/
            integration/
            end_to_end/
            security/
            accessibility/
            recommendations/
            performance/

        scripts/
            deployment/
            backup/
            restore/
            maintenance/

        docs/
            product.md
            requirements.md
            architecture.md
            database.md
            design-system.md
            recommendation-engine.md
            integrations.md
            conversational-profiles.md
            privacy.md
            security.md
            accessibility.md
            deployment.md
            recovery.md
            moderation.md
            testing.md
            operations.md
            decisions/

        tasks/
            README.md

        .github/
            workflows/

Group related interest domains within the catalogue and personal-library modules unless separate Django applications provide a demonstrated benefit.

Do not create one application per page merely because the product has 20 pages.

Create only files and abstractions that have an actual responsibility.

---

# 23. Deployment strategy

Target zero initial expenditure without sacrificing portability.

Evaluate current availability and restrictions of:

- Render for application hosting.
- Neon for PostgreSQL.
- Cloudflare R2 for media storage.
- Cloudflare for DNS and CDN.
- An appropriate transactional email provider.
- GitHub Actions for CI.
- Sentry or an equivalent error-monitoring solution.

These are candidate providers, not guaranteed free production infrastructure.

Verify current quotas, billing requirements, inactivity policies, cold starts, database extensions, worker support, storage limits and commercial terms before committing to them.

Use environment variables for provider configuration.

Avoid vendor-specific dependencies where practical.

Maintain local development without requiring paid services.

Support migration to alternative PostgreSQL providers and S3-compatible storage.

Do not require a custom domain during development.

Evaluate Docker packaging when deployment requirements justify it.

---

# 24. Testing strategy

Every feature must include appropriate tests.

## Unit tests

- Business rules.
- Validation.
- Normalization.
- Recommendation scoring.
- Permission decisions.
- Import transformations.

## Database tests

- Constraints.
- Uniqueness.
- Transactions.
- Deletion policies.
- Migration correctness.

## Integration tests

- External provider responses.
- Provider failures.
- Entity resolution.
- Background processing.
- Media handling.
- Search.
- Recommendation generation.

## End-to-end tests

- Registration.
- Onboarding.
- Adding favourites.
- Automatic metadata retrieval.
- Receiving recommendations.
- Managing all personal pages.
- Creating collections.
- Following.
- Privacy controls.
- Imports.
- Exports.
- Account deletion.

## Security tests

- Cross-user authorization.
- Private media access.
- Search leakage.
- Recommendation leakage.
- Block bypass attempts.
- Malicious uploads.
- Malicious imports.
- Session security.
- Conversational prompt injection.
- Unauthorized conversational retrieval.

## Accessibility tests

- Keyboard-only operation.
- Focus order.
- Form labels.
- Screen reader semantics.
- Contrast.
- Responsive layouts.
- Error announcements.

## Recommendation tests

- Cross-domain relevance.
- Factual relationship correctness.
- Explanation accuracy.
- Cold-start behaviour.
- Diversity.
- Duplicate prevention.
- Negative feedback.
- Missing metadata.
- Privacy enforcement.

## Recovery tests

- Database backup.
- Database restoration.
- Media restoration.
- Provider migration.
- Worker failure recovery.
- Failed deployment rollback.

Do not use mocked tests as the sole evidence that real integrations work.

---

# 25. Performance and reliability

Proposed initial targets:

- WCAG 2.2 AA accessibility.
- Largest Contentful Paint at p75 no greater than 2.5 seconds.
- Interaction to Next Paint at p75 no greater than 200 milliseconds.
- Cumulative Layout Shift at p75 no greater than 0.1.
- Indexed internal search at p95 no greater than 500 milliseconds under a documented test workload.
- Bounded recommendation generation latency.
- No unbounded synchronous external requests.
- No N+1 queries on common catalogue pages.
- Daily backups.
- Recovery point objective of 24 hours.
- Recovery time objective of four hours.

These are acceptance targets, not achieved results.

Benchmark on actual deployment infrastructure.

Document targets that free infrastructure cannot meet.

Use pagination, appropriate indexes, efficient queries, precomputed embeddings, bounded caches and responsive images.

Do not introduce additional infrastructure before profiling demonstrates a need.

---

# 26. Production operations

Implement:

- Health checks.
- Structured logging.
- Error monitoring.
- Database monitoring.
- Storage monitoring.
- Provider quota monitoring.
- Background-job monitoring.
- Backup verification.
- Security-event monitoring.
- Deployment smoke tests.
- Migration procedures.
- Rollback procedures.
- Incident response.
- Data restoration procedures.
- Dependency maintenance.
- Secret rotation.

Do not log private user content unnecessarily.

Use explicit retention policies.

Maintain separate development, testing and production configurations.

Never deploy using Django's development server.

---

# 27. Legal and moderation requirements

Before public launch, document and verify:

- Applicable privacy laws.
- Applicable intermediary obligations.
- User consent.
- Terms of service.
- Community guidelines.
- Copyright procedures.
- Content reporting.
- Moderation procedures.
- Appeals.
- Data retention.
- Account deletion.
- External provider licensing.
- Image licensing.
- Commercial-use restrictions.
- Age eligibility and associated safety obligations.

Obtain appropriate legal review where required.

Do not represent generated legal documents as verified legal compliance.

---

# 28. Explicitly excluded technologies

Do not introduce without a documented requirement:

- React.
- Next.js.
- Tailwind CSS.
- Bootstrap.
- Microservices.
- Kubernetes.
- MongoDB.
- Elasticsearch.
- Dedicated graph databases.
- Dedicated vector databases.
- Redis.
- Celery.
- GraphQL.
- WebSockets.
- LangChain.
- Paid LLM dependencies.
- GPU infrastructure.
- Complex event buses.
- Separate frontend deployment.

Reconsider an exclusion only when measured requirements demonstrate a genuine need.

---

# 29. Implementation roadmap

Generate detailed sequential tasks covering all of the following phases.

1. Product requirements and acceptance criteria.
2. Architecture decisions.
3. Database design.
4. Provider feasibility and licensing verification.
5. Development environment.
6. Repository and quality tooling.
7. Shared frontend design system.
8. Custom user model.
9. Authentication.
10. Profiles and privacy policies.
11. Shared catalogue.
12. External identifiers and provenance.
13. Provider adapters.
14. Personal library management.
15. Books.
16. Movies.
17. TV Shows.
18. Music.
19. History.
20. Culture & Heritage.
21. Travel.
22. Food & Cuisine.
23. Languages.
24. Mythology & Folklore.
25. Philosophy & Psychology.
26. Activities & Experiences.
27. Learning & Exploration.
28. Photography & Memories.
29. Collections.
30. Favourites.
31. Lifetime Bucket List.
32. Statistics.
33. Personal Timeline.
34. Global search.
35. Cross-provider entity resolution.
36. Knowledge graph.
37. Content-based recommendations.
38. Cross-domain recommendation generation.
39. Semantic embedding evaluation.
40. Semantic recommendations.
41. Recommendation ranking.
42. Recommendation explanations.
43. Discover page.
44. Recommendation feedback.
45. Recommendation evaluation.
46. Following and follow requests.
47. Public profile discovery.
48. Shared interests.
49. Blocking and reporting.
50. Moderation.
51. Notifications.
52. Imports.
53. Exports.
54. Account deletion.
55. Media processing and storage.
56. Background processing.
57. Optional conversational profiles.
58. Accessibility verification.
59. Security verification.
60. Performance verification.
61. Deployment infrastructure.
62. Backup and recovery.
63. Operational monitoring.
64. Complete regression testing.
65. Private beta.
66. Production readiness review.
67. Public release.

This list defines scope, not an immutable dependency order.

Reorder tasks according to real dependencies.

Implement security, privacy, media safety and testing throughout development rather than postponing them until final verification.

Build an early end-to-end vertical slice containing account creation, saving a book or movie, automatic metadata retrieval and cross-domain recommendations.

Use that slice to validate architectural assumptions before duplicating the implementation across every domain.

Do not remove any approved feature from the complete product backlog.

---

# 30. Task specification format

Every implementation task must contain:

- Unique task identifier.
- Title.
- Problem being solved.
- Purpose.
- Dependencies.
- Prerequisites.
- Scope.
- Explicitly excluded scope.
- Relevant architecture decisions.
- Files to create or modify.
- Database changes.
- Implementation instructions.
- Security considerations.
- Privacy considerations.
- Accessibility considerations.
- Failure handling.
- Required tests.
- Acceptance criteria.
- Verification commands.
- Documentation updates.
- Definition of done.
- Rollback considerations where applicable.

Tasks must give maintainers enough detail to implement and verify a change.

Avoid giant tasks containing unrelated features.

Do not mark a task complete until its acceptance criteria have been verified.

---

# 32. Definition of production-ready

Lokam is production-ready only when:

- Users can independently register and recover accounts.
- Users can create and manage their personal websites.
- All 20 personal pages function.
- Metadata and images can be retrieved from supported providers.
- Manual entry remains available.
- Cross-domain recommendations function with a single user.
- Recommendation explanations are accurate.
- Privacy is consistently enforced.
- Search does not leak private information.
- Social functionality works safely.
- Media uploads are secure.
- Imports and exports work.
- Account deletion works.
- External provider failures are handled.
- Accessibility requirements are verified.
- Critical security tests pass.
- Backups can actually be restored.
- Deployment and rollback procedures work.
- Operational monitoring exists.
- Applicable licensing and legal requirements are addressed.
- Known limitations are documented.

Optional conversational AI must remain disabled in production unless its separate privacy, security, quality and operational requirements are satisfied.

A functioning interface alone is not production readiness.
