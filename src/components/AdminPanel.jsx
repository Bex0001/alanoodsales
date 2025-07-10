import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '@/contexts/AuthContext'
import { PlusCircle, Edit, Trash2, User, Users, DollarSign, Settings } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

function AdminPanel() {
  const { token, user } = useAuth()
  const [activeTab, setActiveTab] = useState('users')
  const [data, setData] = useState({
    users: [],
    teams: [],
    kpis: [],
    marketingBudget: null,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  const fetchData = async (endpoint, key) => {
    try {
      const response = await fetch(`${API_BASE}/admin/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) {
        throw new Error(`فشل في جلب بيانات ${key}`)
      }
      const result = await response.json()
      setData(prev => ({ ...prev, [key]: result }))
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    if (user && (user.role === 'admin' || user.role === 'sales_manager')) {
      setLoading(true)
      Promise.all([
        fetchData('users', 'users'),
        fetchData('teams', 'teams'),
        fetchData('kpis', 'kpis'),
        // fetchData('marketing-budget?month=1&year=2025', 'marketingBudget'), // مثال لجلب ميزانية شهر معين
      ]).finally(() => setLoading(false))
    } else {
      setError('ليس لديك صلاحية لعرض هذه الصفحة.')
      setLoading(false)
    }
  }, [token, user])

  if (loading) return <div className="text-center py-8">جاري تحميل لوحة الإدارة...</div>
  if (error) return <div className="text-center py-8 text-red-500">خطأ: {error}</div>

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">لوحة الإدارة</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="users"><User className="ml-2 h-4 w-4" /> المستخدمون</TabsTrigger>
          <TabsTrigger value="teams"><Users className="ml-2 h-4 w-4" /> الفرق</TabsTrigger>
          <TabsTrigger value="kpis"><Settings className="ml-2 h-4 w-4" /> مؤشرات الأداء</TabsTrigger>
          <TabsTrigger value="marketing"><DollarSign className="ml-2 h-4 w-4" /> ميزانية التسويق</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>إدارة المستخدمين</CardTitle>
              <Button className="apple-button"><PlusCircle className="ml-2 h-4 w-4" /> إضافة مستخدم</Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>اسم المستخدم</TableHead>
                    <TableHead>البريد الإلكتروني</TableHead>
                    <TableHead>الدور</TableHead>
                    <TableHead>الحالة</TableHead>
                    <TableHead className="text-center">الإجراءات</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.users.map(userItem => (
                    <TableRow key={userItem.id}>
                      <TableCell>{userItem.username}</TableCell>
                      <TableCell>{userItem.email}</TableCell>
                      <TableCell>{userItem.role}</TableCell>
                      <TableCell>{userItem.is_active ? 'نشط' : 'غير نشط'}</TableCell>
                      <TableCell className="text-center">
                        <Button variant="ghost" size="sm" className="ml-2"><Edit className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm" className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="teams">
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>إدارة الفرق</CardTitle>
              <Button className="apple-button"><PlusCircle className="ml-2 h-4 w-4" /> إضافة فريق</Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>اسم الفريق</TableHead>
                    <TableHead>القائد</TableHead>
                    <TableHead>الوصف</TableHead>
                    <TableHead className="text-center">الإجراءات</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.teams.map(team => (
                    <TableRow key={team.id}>
                      <TableCell>{team.name}</TableCell>
                      <TableCell>{team.leader_name || 'لا يوجد'}</TableCell>
                      <TableCell>{team.description || 'لا يوجد'}</TableCell>
                      <TableCell className="text-center">
                        <Button variant="ghost" size="sm" className="ml-2"><Edit className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm" className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kpis">
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>إدارة مؤشرات الأداء (KPIs)</CardTitle>
              <Button className="apple-button"><PlusCircle className="ml-2 h-4 w-4" /> إضافة مؤشر</Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>الاسم</TableHead>
                    <TableHead>الوصف</TableHead>
                    <TableHead>الوزن</TableHead>
                    <TableHead>الحد الأقصى للنقاط</TableHead>
                    <TableHead className="text-center">الإجراءات</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.kpis.map(kpi => (
                    <TableRow key={kpi.id}>
                      <TableCell>{kpi.name}</TableCell>
                      <TableCell>{kpi.description || 'لا يوجد'}</TableCell>
                      <TableCell>{kpi.weight}</TableCell>
                      <TableCell>{kpi.max_score}</TableCell>
                      <TableCell className="text-center">
                        <Button variant="ghost" size="sm" className="ml-2"><Edit className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm" className="text-red-500"><Trash2 className="h-4 w-4" /></Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="marketing">
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>إدارة ميزانية التسويق</CardTitle>
              <Button className="apple-button"><PlusCircle className="ml-2 h-4 w-4" /> تحديد ميزانية</Button>
            </CardHeader>
            <CardContent>
              {/* سيتم إضافة واجهة لتحديد وعرض ميزانية التسويق هنا */}
              <p className="text-muted-foreground">واجهة إدارة ميزانية التسويق قيد التطوير...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AdminPanel


