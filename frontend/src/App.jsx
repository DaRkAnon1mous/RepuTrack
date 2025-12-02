import { SignedIn, SignedOut, SignIn, UserButton } from '@clerk/clerk-react'
import { useUser, useClerk } from '@clerk/clerk-react'
import { useState, useEffect } from 'react'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:8000'

function Dashboard() {
  const { user } = useUser()
  const { getToken } = useClerk()
  const [products, setProducts] = useState([])

  useEffect(() => {
    const load = async () => {
      const token = await getToken({ template: 'fastapi' })
      const res = await axios.get('/api/products', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setProducts(res.data)
    }
    load()
  }, [getToken])

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-12">
          <h1 className="text-5xl font-bold text-white">
            Welcome, {user?.firstName || 'User'}!
          </h1>
          <UserButton afterSignOutUrl="/"/>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {products.length === 0 ? (
            <p className="text-xl text-gray-300 col-span-3 text-center">
              No products yet. Add one from the API docs!
            </p>
          ) : (
            products.map(p => (
              <div key={p.id} className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                <h3 className="text-2xl font-bold text-white">{p.name}</h3>
                <p className="text-gray-300 mt-2">{p.links.length} links tracked</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <>
      <SignedIn>
        <Dashboard />
      </SignedIn>

      <SignedOut>
        <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-12 shadow-2xl max-w-md w-full border border-white/20">
            <h1 className="text-5xl font-bold text-white text-center mb-10">RepuTrack</h1>
            <SignIn
              routing="path"
              path="/sign-in"
              signUpUrl="/sign-up"
              afterSignInUrl="/"
            />
          </div>
        </div>
      </SignedOut>
    </>
  )
}