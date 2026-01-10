import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { getAuthMe, getDriverAuthMe, loginDriver as apiLoginDriver } from '../lib/api'
import type { AuthMe } from '../lib/types'

type AuthType = 'api-key' | 'jwt'

type AuthState = {
  apiKey: string
  profile: AuthMe | null
  loading: boolean
  error: string | null
  authType: AuthType | null
  login: (key: string) => Promise<void>
  loginDriver: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | undefined>(undefined)

const STORAGE_KEY_API = 'safedrive_api_key'
const STORAGE_KEY_JWT = 'safedrive_jwt_token'
const STORAGE_KEY_AUTH_TYPE = 'safedrive_auth_type'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKey] = useState(() => {
    return localStorage.getItem(STORAGE_KEY_API) ?? ''
  })
  const [jwtToken, setJwtToken] = useState(() => {
    return localStorage.getItem(STORAGE_KEY_JWT) ?? ''
  })
  const [authType, setAuthType] = useState<AuthType | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY_AUTH_TYPE)
    return (stored as AuthType) || null
  })
  const [profile, setProfile] = useState<AuthMe | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProfile = useCallback(
    async (key: string, token: string, type: AuthType) => {
      if (!key && !token) {
        setProfile(null)
        setLoading(false)
        return
      }
      setLoading(true)
      try {
        let data: AuthMe
        if (type === 'jwt') {
          data = await getDriverAuthMe(token)
        } else {
          data = await getAuthMe(key)
        }
        setProfile(data)
        setError(null)
        return data
      } catch (err) {
        setProfile(null)
        const message = err instanceof Error ? err.message : 'Authentication failed'
        setError(message)
        throw new Error(message)
      } finally {
        setLoading(false)
      }
    },
    [setProfile],
  )

  useEffect(() => {
    if (!apiKey && !jwtToken) {
      setLoading(false)
      return
    }
    const type = authType || 'api-key'
    loadProfile(apiKey, jwtToken, type).catch(() => undefined)
  }, [apiKey, jwtToken, authType, loadProfile])

  const login = useCallback(
    async (key: string) => {
      const trimmed = key.trim()
      setApiKey(trimmed)
      setAuthType('api-key')
      localStorage.setItem(STORAGE_KEY_API, trimmed)
      localStorage.setItem(STORAGE_KEY_AUTH_TYPE, 'api-key')
      localStorage.removeItem(STORAGE_KEY_JWT)
      setJwtToken('')
      try {
        await loadProfile(trimmed, '', 'api-key')
      } catch (err) {
        localStorage.removeItem(STORAGE_KEY_API)
        localStorage.removeItem(STORAGE_KEY_AUTH_TYPE)
        setApiKey('')
        setAuthType(null)
        throw err
      }
    },
    [loadProfile],
  )

  const loginDriver = useCallback(
    async (email: string, password: string) => {
      setLoading(true)
      setError(null)
      try {
        const response = await apiLoginDriver(email, password)
        const token = response.access_token
        setJwtToken(token)
        setAuthType('jwt')
        localStorage.setItem(STORAGE_KEY_JWT, token)
        localStorage.setItem(STORAGE_KEY_AUTH_TYPE, 'jwt')
        localStorage.removeItem(STORAGE_KEY_API)
        setApiKey('')
        await loadProfile('', token, 'jwt')
      } catch (err) {
        localStorage.removeItem(STORAGE_KEY_JWT)
        localStorage.removeItem(STORAGE_KEY_AUTH_TYPE)
        setJwtToken('')
        setAuthType(null)
        throw err
      }
    },
    [loadProfile],
  )

  const logout = useCallback(() => {
    setApiKey('')
    setJwtToken('')
    setAuthType(null)
    setProfile(null)
    setError(null)
    localStorage.removeItem(STORAGE_KEY_API)
    localStorage.removeItem(STORAGE_KEY_JWT)
    localStorage.removeItem(STORAGE_KEY_AUTH_TYPE)
  }, [])

  const value = useMemo(
    () => ({
      apiKey: authType === 'api-key' ? apiKey : jwtToken,
      profile,
      loading,
      error,
      authType,
      login,
      loginDriver,
      logout,
    }),
    [apiKey, jwtToken, profile, loading, error, authType, login, loginDriver, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
