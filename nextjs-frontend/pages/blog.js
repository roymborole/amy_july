import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Blog() {
  const router = useRouter()

  useEffect(() => {
    router.push('/')
  }, [router])  // Add router to the dependency array

  return null
}