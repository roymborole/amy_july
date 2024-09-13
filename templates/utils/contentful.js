import { createClient } from 'contentful'

const client = createClient({
  space: process.env.CONTENTFUL_SPACE_ID,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN,
})

export const getFeaturedArticle = async () => {
  const response = await client.getEntries({
    content_type: 'featuredArticle',
    limit: 1,
    include: 2,
  })
  return response.items[0]?.fields.article
}

export const getTopStories = async (limit = 5) => {
  const response = await client.getEntries({
    content_type: 'article',
    limit,
    order: '-sys.createdAt',
  })
  return response.items
}