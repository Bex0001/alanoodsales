import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/contexts/AuthContext'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const { login } = useAuth()

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    const endpoint = isRegistering ? 'auth/register' : 'auth/login'
    const body = isRegistering ? { username, email, password } : { username, password }

    try {
      const response = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'فشل في العملية')
      }

      if (!isRegistering) {
        login(data.user, data.access_token)
      } else {
        alert('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.')
        setIsRegistering(false)
        setUsername('')
        setEmail('')
        setPassword('')
      }
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900" dir="rtl">
      <Card className="w-full max-w-md apple-card">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {isRegistering ? 'إنشاء حساب جديد' : 'تسجيل الدخول'}
          </CardTitle>
          <CardDescription className="text-gray-600 dark:text-gray-400">
            {isRegistering ? 'أدخل بياناتك لإنشاء حساب' : 'أدخل اسم المستخدم وكلمة المرور'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="username">اسم المستخدم</Label>
              <Input
                id="username"
                type="text"
                placeholder="اسم المستخدم"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            {isRegistering && (
              <div>
                <Label htmlFor="email">البريد الإلكتروني</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="البريد الإلكتروني"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
            )}
            <div>
              <Label htmlFor="password">كلمة المرور</Label>
              <Input
                id="password"
                type="password"
                placeholder="كلمة المرور"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <Button type="submit" className="w-full apple-button">
              {isRegistering ? 'تسجيل' : 'تسجيل الدخول'}
            </Button>
          </form>
          <div className="mt-6 text-center">
            <Button variant="link" onClick={() => setIsRegistering(!isRegistering)} className="text-blue-600 dark:text-blue-400">
              {isRegistering ? 'لدي حساب بالفعل؟ تسجيل الدخول' : 'ليس لدي حساب؟ إنشاء حساب'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login


