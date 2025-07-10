import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { useAuth } from '@/contexts/AuthContext'
import { Download, Filter, Search } from 'lucide-react'

function ReportsCenter() {
  const { token, user } = useAuth()
  const [reportType, setReportType] = useState('sales_performance')
  const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1)
  const [filterYear, setFilterYear] = useState(new Date().getFullYear())
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  const fetchReportData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/reports/${reportType}?month=${filterMonth}&year=${filterYear}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) {
        throw new Error('فشل في جلب بيانات التقرير')
      }
      const data = await response.json()
      setReportData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchReportData()
    }
  }, [reportType, filterMonth, filterYear, user])

  const renderReport = () => {
    if (loading) return <div className="text-center py-8">جاري تحميل التقرير...</div>
    if (error) return <div className="text-center py-8 text-red-500">خطأ: {error}</div>
    if (!reportData) return <div className="text-center py-8">اختر نوع التقرير والفلاتر لعرض البيانات.</div>

    switch (reportType) {
      case 'sales_performance':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={reportData.employee_performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="sales" fill="#8884d8" name="المبيعات" />
              <Bar dataKey="target" fill="#82ca9d" name="الهدف" />
            </BarChart>
          </ResponsiveContainer>
        )
      case 'commission_summary':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={reportData.commission_distribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={150}
                fill="#8884d8"
                dataKey="commission"
                nameKey="name"
              >
                {reportData.commission_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042'][index % 4]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )
      case 'marketing_impact':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={reportData.marketing_impact_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="social_media_sales" stroke="#8884d8" name="مبيعات السوشيال ميديا" />
              <Line type="monotone" dataKey="marketing_cost" stroke="#82ca9d" name="تكلفة التسويق" />
            </LineChart>
          </ResponsiveContainer>
        )
      default:
        return <div className="text-center py-8">اختر نوع التقرير.</div>
    }
  }

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">مركز التقارير</h1>

      <Card className="apple-card">
        <CardHeader>
          <CardTitle>مولد التقارير</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">نوع التقرير</label>
              <Select value={reportType} onValueChange={setReportType}>
                <SelectTrigger>
                  <SelectValue placeholder="اختر نوع التقرير" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sales_performance">أداء المبيعات</SelectItem>
                  <SelectItem value="commission_summary">ملخص العمولات</SelectItem>
                  <SelectItem value="marketing_impact">تأثير التسويق</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">الشهر</label>
              <Input type="number" value={filterMonth} onChange={(e) => setFilterMonth(e.target.value)} min="1" max="12" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">السنة</label>
              <Input type="number" value={filterYear} onChange={(e) => setFilterYear(e.target.value)} min="2020" max="2030" />
            </div>
          </div>
          <div className="flex justify-end space-x-2 space-x-reverse">
            <Button onClick={fetchReportData} disabled={loading} className="apple-button">
              <Search className="ml-2 h-4 w-4" /> عرض التقرير
            </Button>
            <Button variant="outline" className="apple-button">
              <Download className="ml-2 h-4 w-4" /> تحميل PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="apple-card">
        <CardHeader>
          <CardTitle>نتائج التقرير</CardTitle>
        </CardHeader>
        <CardContent>
          {renderReport()}
        </CardContent>
      </Card>
    </div>
  )
}

export default ReportsCenter


