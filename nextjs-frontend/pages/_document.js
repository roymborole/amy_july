import Document, { Html, Head, Main, NextScript } from 'next/document'

class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
        <div id="ticker-tape-root"></div>
          <link
            href="https://fonts.googleapis.com/css2?family=Anton&family=Roboto:wght@400;700&display=swap"
            rel="stylesheet"
          />
        </Head>
        <body>
          <Main />
          <NextScript />
          <script src="/static/SearchModule.js" async></script>
        </body>
      </Html>
    )
  }
}

export default MyDocument

