import '../styles/globals.css';
import TickerTape from '../components/Tickertape';

function MyApp({ Component, pageProps }) {
  return (
    <>
      <TickerTape />
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;