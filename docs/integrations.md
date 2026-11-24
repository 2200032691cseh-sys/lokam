# Provider feasibility

Official documentation reviewed November 24, 2026. This is a document review. Account entitlements, current terms acceptance, live API calls, storage permissions and commercial rights remain launch checks.

| Provider | Documented capability and design consequence |
|---|---|
| Open Library | Works, editions, authors, subjects, ISBN/search and cover references. Default 1 request/s or 3 with identification. Target low volume, no bulk API harvesting. Verify cover delivery rights separately. [API](https://openlibrary.org/developers/api) |
| Screen metadata | Wikidata entity search and structured claims provide film and TV metadata without credentials. Coverage varies for episodes, artwork and provider suggestions. [Data access](https://www.wikidata.org/wiki/Wikidata:Data_access) |
| MusicBrainz and Cover Art Archive | MusicBrainz supports artists, releases, recordings, works and relations. Use an identifying agent and 1 request/s, and verify commercial terms and field-level data licence. Cover Art Archive supplies references; check copyright before public display or copying. [API](https://musicbrainz.org/doc/MusicBrainz_API) · [Cover archive](https://musicbrainz.org/doc/Cover_Art_Archive) |
| Wikidata | Principal external structured graph. Target QIDs and known properties; record statement IDs, qualifiers, rank, sources and revision. Structured data is CC0. Wikidata statement presence alone does not establish fact; review predicate and evidence, especially disputed history. Avoid live heavy SPARQL in requests. [Data access](https://www.wikidata.org/wiki/Wikidata:Data_access) |
| Wikipedia, Wikivoyage, Wiktionary, Commons | Prefer source links; copied summaries or text need attribution and applicable share-alike verification. Check each Commons file's licence, attribution and restrictions. [Wikimedia terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) · [Commons reuse](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) |
| OpenStreetMap and Leaflet | Map tiles and underlying data have separate policies. For public OSM tiles, attribution, cache, referrer and no bulk/offline fetch apply; capacity is best effort. Use a configurable source and destination list; verify actual tile capacity before launch. [Tile policy](https://operations.osmfoundation.org/policies/tiles/) · [Leaflet](https://leafletjs.com/) |
| RSS/Atom | Use reviewed public feeds or manual source links. Limit parsed bytes, entries and retention, disable external entity resolution, and check per-feed reuse rights. |
| Goodreads and Letterboxd | User-uploaded exports only. Exact export schema, versions, field coverage and fixture availability are unverified. Sample current files with consent and sanitize fixtures. Map statuses, ratings and permitted notes; ignore personal activity dates. [Goodreads help](https://help.goodreads.com/s/article/How-do-I-import-or-export-my-books-1553870934590) · [Letterboxd help](https://letterboxd.com/about/faq/) |

Letterboxd confirms a ZIP of CSV files that can include deleted content. Import only selected supported members from a bounded archive and exclude deleted records by default. Goodreads' official help page content was unavailable during review; exact supported format remains unverified. [Letterboxd account export](https://support.letterboxd.com/hc/en-us/articles/15179196880911-Can-I-get-a-copy-of-my-account-data)

MusicBrainz licenses core data under CC0 and supplementary data under CC BY-NC-SA 3.0. Commercial web-service access is a separate issue. Check which fields are supplementary and retain their attribution and redistribution requirements. [Data licence](https://musicbrainz.org/doc/About/Data_License) · [API terms FAQ](https://musicbrainz.org/doc/MusicBrainz_API/FAQ)

Adapters use a common typed candidate schema and per-provider auth, allowlists, deadlines, quotas, Retry-After, bounded retries, validated responses, source metadata and kill switches. Keep cache TTLs and display/copy/export permissions per provider and field. Keep secret keys server-side. Record supported rights, region and cache duration before enabling. Use placeholders/source links when rights or assets are missing. Validate credentials and one real read per enabled capability after approval. Manual owner-only entry and curated source links address sparse data for food, heritage, regional languages, traditions, local venues and experiences.

## Initial adapter gates

The adapters support Open Library work search and Wikidata film and TV search. They validate entity classes and record the selected title, year and source revision. Run `uv run --env-file .env python manage.py check_catalogue_provider book` and repeat for `movie` and `tv-show` to verify live reads without saving catalogue records.

| Source | Fields eligible for initial ingestion | Held pending verification |
|---|---|---|
| Open Library | Work and edition IDs, ISBN, title, authors, publication year, language and factual subject references, with source provenance. Use at most one request per second until a maintainer contact is configured. | Long descriptions and cover redisplay or storage pending field and asset rights review. [Licensing](https://openlibrary.org/developers/licensing) |
| Film and TV via Wikidata | Persist matched QIDs, labels, release years and source revisions. | Credits, episode coverage and images require field-specific enrichment. Wikidata does not supply editorial recommendations. [Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) |
| Wikidata | QIDs, labels and targeted CC0 statements, references and qualifiers. | Individual graph assertions need evidence review. Linked images and third-party source text retain separate rights. [Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) |

Only persist fields whose policy is recorded. Attach source identifiers and retrieval time. Exclude provider payloads from personal export unless redistribution is expressly permitted. Live credentials and terms acceptance must precede credentialed source enablement.
