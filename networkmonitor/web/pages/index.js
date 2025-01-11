import Head from 'next/head'
import NetworkDashboard from '../components/NetworkDashboard'

const Home = () => {
  return (
    <div>
      <Head>
        <title>Network Monitor Dashboard</title>
        <meta name="description" content="Network monitoring and control dashboard" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <NetworkDashboard />
      </main>
    </div>
  )
}

export default Home