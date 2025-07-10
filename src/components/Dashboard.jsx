import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { useAuth } from '@/contexts/AuthContext'

function Dashboard() {
  const { token } = useAuth()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch(`${API_BASE}/dashboard`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (!response.ok) {
          throw new Error('فشل في جلب بيانات لوحة التحكم')
        }
        const data = await response.json()
        setDashboardData(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [token])

  if (loading) return <div className="text-center py-8">جاري تحميل لوحة التحكم...</div>
  if (error) return <div className="text-center py-8 text-red-500">خطأ: {error}</div>
  if (!dashboardData) return <div className="text-center py-8">لا توجد بيانات لعرضها.</div>

  const salesByProduct = dashboardData.sales_by_product || [
    { name: 'حديد إنشائي', value: 400 },
    { name: 'حديد ديكور', value: 300 },
    { name: 'خشب', value: 300 },
    { name: 'ألومنيوم', value: 200 },
  ]

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">لوحة التحكم الرئيسية</h1>

      {/* KPIs Widgets */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">إجمالي المبيعات</CardTitle>
            <BarChart2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.total_sales?.toLocaleString() || '0'} ريال</div>
            <p className="text-xs text-muted-foreground">+20.1% عن الشهر الماضي</p>
          </CardContent>
        </Card>
        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">نسبة تحقيق الهدف</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.target_achievement_rate?.toFixed(2) || '0'}%</div>
            <p className="text-xs text-muted-foreground">الهدف الشهري: {dashboardData.monthly_target?.toLocaleString() || '0'} ريال</p>
          </CardContent>
        </Card>
        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">عدد المشاريع الموقعة</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.signed_projects_count || '0'}</div>
            <p className="text-xs text-muted-foreground">+15 مشروع جديد هذا الشهر</p>
          </CardContent>
        </Card>
        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">متوسط قيمة الصفقة</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.average_deal_value?.toLocaleString() || '0'} ريال</div>
            <p className="text-xs text-muted-foreground">زيادة 5% عن الربع السابق</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="apple-card">
          <CardHeader>
            <CardTitle>المبيعات حسب نوع المنتج</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={salesByProduct}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {salesByProduct.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="apple-card">
          <CardHeader>
            <CardTitle>أفضل المندوبين (مبيعات)</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={dashboardData.top_performers || [
                  { name: 'أحمد', sales: 120000 },
                  { name: 'فاطمة', sales: 100000 },
                  { name: 'محمد', sales: 90000 },
                  { name: 'سارة', sales: 80000 },
                ]}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="sales" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Sales by Region (Placeholder for interactive map) */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle>المبيعات حسب المنطقة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            (سيتم دمج خريطة تفاعلية هنا لاحقاً)
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard


