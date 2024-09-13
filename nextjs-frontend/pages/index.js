import { getFeaturedArticle, getTopStories } from '../utils/contentful';
import Link from 'next/link';
import Image from 'next/image';
import SearchBar from '../components/SearchBar';

export async function getStaticProps() {
  try {
    const featuredArticle = await getFeaturedArticle();
    const topStories = await getTopStories(5);
    console.log('Featured Article:', JSON.stringify(featuredArticle, null, 2));
    console.log('Top Stories:', JSON.stringify(topStories, null, 2));
    return {
      props: { featuredArticle, topStories },
    };
  } catch (error) {
    console.error("Error fetching data:", error);
    return {
      props: { error: 'Error fetching data from Contentful' },
    };
  }
}

export default function Home({ error, featuredArticle, topStories }) {
  if (error) {
    return <div className="text-red-500 p-4">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-custom-bg text-white font-roboto">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-anton mb-6 text-center">Demystifying Finance One Click at a Time</h1>
        
        <div className="flex flex-col md:flex-row gap-8">
          {/* Featured Article */}
          <div className="md:w-2/3">
            {featuredArticle && featuredArticle.fields && featuredArticle.fields.article && (
              <div className="bg-custom-interior p-6 rounded-lg">
                {featuredArticle.fields.article.fields.image && 
                 featuredArticle.fields.article.fields.image.fields &&
                 featuredArticle.fields.article.fields.image.fields.file && (
                  <div className="mb-4">
                    <Image
                      src={`https:${featuredArticle.fields.article.fields.image.fields.file.url}`}
                      alt={featuredArticle.fields.article.fields.image.fields.title || 'Featured Article'}
                      width={featuredArticle.fields.article.fields.image.fields.file.details.image.width}
                      height={featuredArticle.fields.article.fields.image.fields.file.details.image.height}
                      layout="responsive"
                    />
                  </div>
                )}
                <h2 className="text-2xl font-anton mb-4">
                  {featuredArticle.fields.article.fields.title || 'Featured Article'}
                </h2>
                <p className="mb-4">
                  {(featuredArticle.fields.article.fields.description || '').substring(0, 200)}...
                </p>
                <Link 
                  href={`/article/${featuredArticle.fields.article.sys.id}`} 
                  className="text-blue-400 hover:underline"
                >
                  Read more
                </Link>
              </div>
            )}
          </div>
          
          {/* Top Stories */}
          <div className="md:w-1/3">
            <div className="bg-custom-stories p-6 rounded-lg">
              <h2 className="text-2xl font-anton mb-4">TOP STORIES</h2>
              <ul className="space-y-4">
                {topStories && topStories.map((story) => (
                  <li key={story.sys.id} className="flex items-center">
                    {story.fields.image && 
                     story.fields.image.fields &&
                     story.fields.image.fields.file && (
                      <div className="w-16 h-16 mr-4 relative overflow-hidden rounded">
                        <Image
                          src={`https:${story.fields.image.fields.file.url}`}
                          alt={story.fields.image.fields.title || 'Story Image'}
                          layout="fill"
                          objectFit="cover"
                        />
                      </div>
                    )}
                    <Link 
                      href={`/article/${story.sys.id}`} 
                      className="hover:underline"
                    >
                      {story.fields.title || 'Untitled Story'}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <SearchBar />
        </div>
      </div>
    </div>
  );
}