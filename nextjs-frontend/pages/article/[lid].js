import Image from 'next/image';
import { useRouter } from 'next/router';
import { getEntry } from '../../utils/contentful';

export async function getStaticPaths() {
  return { paths: [], fallback: 'blocking' }
}

export async function getStaticProps({ params }) {
  const article = await getEntry(params.id);
  return {
    props: { article },

  }
}

export default function Article({ article }) {
  const router = useRouter();

  if (router.isFallback) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h1>{article.fields.title}</h1>
      <p>{article.fields.description}</p>
      {article.fields.image && 
       article.fields.image.fields && 
       article.fields.image.fields.file && (
        <Image 
          src={`https:${article.fields.image.fields.file.url}`}
          alt={article.fields.image.fields.title || 'Article image'}
          width={500}
          height={300}
          layout="responsive"
        />
      )}
    </div>
  )
}