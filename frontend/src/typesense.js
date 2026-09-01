import Typesense from 'typesense';

// Search-only key -- safe to ship to the browser since it can only read,
// never write or delete, unlike the admin key used in index_birds.py
const client = new Typesense.Client({
  nodes: [{
    host: 'localhost',
    port: 8108,
    protocol: 'http',
  }],
  apiKey: 'xyz', // matches TYPESENSE_SEARCH_ONLY_API_KEY in .env
  connectionTimeoutSeconds: 2,
});

// Searches commonName/species/description, typo-tolerant by default.
// Returns a flat array of bird objects shaped like what /api/birds
// returns, so BirdCard doesn't need to know which source it came from.
export async function searchBirds(query) {
  const results = await client.collections('birds').documents().search({
    q: query,
    query_by: 'commonName,species,description',
  });

  return results.hits.map((hit) => hit.document);
}