import { createClient } from 'contentful'

const client = createClient({
  space: process.env.CONTENTFUL_SPACE_ID,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN,
})

export async function getFeaturedArticle() {
  const response = await client.getEntries({
    content_type: 'featuredArticle',
    limit: 1,
    include: 2,
  })
  return response.items[0]
}

export async function getTopStories(limit = 5) {
  const response = await client.getEntries({
    content_type: 'asset',  // Make sure this matches your Contentful content type
    limit,
    order: '-sys.createdAt',
    select: ['sys.id', 'fields.title', 'fields.image']  // Explicitly select the fields you need
  })
  console.log('Raw Top Stories Response:', JSON.stringify(response, null, 2));
  return response.items
}

export async function getEntry(id) {
  return await client.getEntry(id)
}

export async function getAllArticles() {
  const response = await client.getEntries({
    content_type: 'article',
  })
  return response.items
}