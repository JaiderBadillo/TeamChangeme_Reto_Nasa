import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
  Filler,
  type ChartOptions,
} from 'chart.js'
import { Bar, Line, Scatter } from 'react-chartjs-2'
import { Link } from 'react-router-dom'
import { BarChart3, Upload } from 'lucide-react'
import type { DataRow } from '../context/DataStoreContext'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
  Filler,
)

const BASE_TOOLTIP = {
  backgroundColor: '#0A0806',
  borderColor: '#FEB352',
  borderWidth: 1,
  titleColor: '#B7E4F9',
  bodyColor: '#F5EDE4',
  padding: 12,
  cornerRadius: 12,
}

const GRID_COLOR = 'rgba(254, 179, 82, 0.14)'
const TICK_COLOR = '#E2B84D'
const AXIS_TITLE_COLOR = '#B7E4F9'

export function EmptyChartState({
  title = 'No dataset loaded yet',
  subtitle = 'Upload a .json or .csv file in the Data tab (or connect an API endpoint) to populate this Chart.js canvas.',
  heightClass = 'h-[280px]',
}: {
  title?: string
  subtitle?: string
  heightClass?: string
}) {
  return (
    <div
      className={`${heightClass} w-full rounded-2xl border border-dashed border-[#FEB352]/25 bg-black flex flex-col items-center justify-center text-center px-6 gap-3`}
    >
      <div className="w-11 h-11 rounded-full border border-[#B7E4F9]/35 flex items-center justify-center text-[#B7E4F9]">
        <BarChart3 className="w-5 h-5" />
      </div>
      <div className="space-y-1 max-w-md">
        <p className="font-[var(--font-display)] text-lg font-semibold text-[#F5EDE4]">{title}</p>
        <p className="text-xs text-[#9B8F83] leading-relaxed">{subtitle}</p>
      </div>
      <Link
        to="/data"
        className="svg-chip px-4 py-1.5 text-xs inline-flex items-center gap-1.5 hover:border-[#FEB352]"
      >
        <Upload className="w-3.5 h-3.5" /> Connect data in Data tab
      </Link>
    </div>
  )
}

export function DynamicBarChart({
  rows,
  labelColumn,
  valueColumn,
  horizontal = false,
  accentColor = '#FEB352',
}: {
  rows: DataRow[]
  labelColumn: string
  valueColumn: string
  horizontal?: boolean
  accentColor?: string
}) {
  const sliced = rows.slice(0, 24)
  const labels = sliced.map((r, i) => String(r[labelColumn] ?? `#${i + 1}`))
  const values = sliced.map((r) => {
    const v = r[valueColumn]
    return typeof v === 'number' ? v : null
  })

  const data = {
    labels,
    datasets: [
      {
        label: valueColumn,
        data: values,
        backgroundColor: accentColor,
        borderColor: accentColor,
        borderRadius: 8,
        barPercentage: 0.68,
      },
    ],
  }

  const options: ChartOptions<'bar'> = {
    indexAxis: horizontal ? 'y' : 'x',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#F5EDE4', font: { size: 12 } } },
      tooltip: BASE_TOOLTIP,
    },
    scales: {
      x: {
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR, font: { size: 11 } },
        title: {
          display: true,
          text: horizontal ? valueColumn : labelColumn,
          color: AXIS_TITLE_COLOR,
          font: { size: 11, weight: 'bold' },
        },
      },
      y: {
        beginAtZero: true,
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR, font: { size: 11 } },
        title: {
          display: true,
          text: horizontal ? labelColumn : valueColumn,
          color: AXIS_TITLE_COLOR,
          font: { size: 11, weight: 'bold' },
        },
      },
    },
  }

  return (
    <div className="h-[290px] w-full">
      <Bar data={data} options={options} />
    </div>
  )
}

export function DynamicLineChart({
  rows,
  labelColumn,
  valueColumn,
}: {
  rows: DataRow[]
  labelColumn: string
  valueColumn: string
}) {
  const sliced = rows.slice(0, 40)
  const labels = sliced.map((r, i) => String(r[labelColumn] ?? `#${i + 1}`))
  const values = sliced.map((r) => {
    const v = r[valueColumn]
    return typeof v === 'number' ? v : null
  })

  const data = {
    labels,
    datasets: [
      {
        label: valueColumn,
        data: values,
        borderColor: '#FEB352',
        backgroundColor: 'rgba(254, 179, 82, 0.16)',
        pointBackgroundColor: '#B7E4F9',
        pointBorderColor: '#000000',
        pointBorderWidth: 2,
        pointRadius: 5,
        borderWidth: 3,
        tension: 0.25,
        fill: true,
        spanGaps: true,
      },
    ],
  }

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#F5EDE4', font: { size: 12 } } },
      tooltip: BASE_TOOLTIP,
    },
    scales: {
      x: {
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR, font: { size: 11 } },
        title: { display: true, text: labelColumn, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' } },
      },
      y: {
        beginAtZero: true,
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR, font: { size: 11 } },
        title: { display: true, text: valueColumn, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' } },
      },
    },
  }

  return (
    <div className="h-[280px] w-full">
      <Line data={data} options={options} />
    </div>
  )
}

export function DynamicCompareChart({
  rows,
  labelColumn,
  colA,
  colB,
  chartType = 'bar',
}: {
  rows: DataRow[]
  labelColumn: string
  colA: string
  colB: string
  chartType?: 'bar' | 'line'
}) {
  const sliced = rows.slice(0, 24)
  const labels = sliced.map((r, i) => String(r[labelColumn] ?? `#${i + 1}`))
  const seriesA = sliced.map((r) => (typeof r[colA] === 'number' ? (r[colA] as number) : null))
  const seriesB = sliced.map((r) => (typeof r[colB] === 'number' ? (r[colB] as number) : null))

  const barData = {
    labels,
    datasets: [
      {
        label: colA,
        data: seriesA,
        backgroundColor: '#FEB352',
        borderRadius: 8,
      },
      {
        label: colB,
        data: seriesB,
        backgroundColor: '#B7E4F9',
        borderRadius: 8,
      },
    ],
  }

  const lineData = {
    labels,
    datasets: [
      {
        label: colA,
        data: seriesA,
        borderColor: '#FEB352',
        backgroundColor: 'rgba(254, 179, 82, 0.16)',
        pointBackgroundColor: '#FEB352',
        pointRadius: 5,
        borderWidth: 3,
        tension: 0.25,
        spanGaps: true,
      },
      {
        label: colB,
        data: seriesB,
        borderColor: '#B7E4F9',
        backgroundColor: 'rgba(183, 228, 249, 0.16)',
        pointBackgroundColor: '#B7E4F9',
        pointRadius: 5,
        borderWidth: 3,
        tension: 0.25,
        spanGaps: true,
      },
    ],
  }

  const sharedScales = {
    x: {
      grid: { color: GRID_COLOR },
      ticks: { color: TICK_COLOR },
      title: { display: true, text: labelColumn, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' as const } },
    },
    y: {
      beginAtZero: true,
      grid: { color: GRID_COLOR },
      ticks: { color: TICK_COLOR },
      title: { display: true, text: `${colA} / ${colB}`, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' as const } },
    },
  }

  return (
    <div className="h-[300px] w-full">
      {chartType === 'bar' ? (
        <Bar
          data={barData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#F5EDE4' } }, tooltip: BASE_TOOLTIP },
            scales: sharedScales,
          }}
        />
      ) : (
        <Line
          data={lineData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#F5EDE4' } }, tooltip: BASE_TOOLTIP },
            scales: sharedScales,
          }}
        />
      )}
    </div>
  )
}

export function DynamicScatterChart({
  rows,
  xColumn,
  yColumn,
}: {
  rows: DataRow[]
  xColumn: string
  yColumn: string
}) {
  const pts = rows
    .filter((r) => typeof r[xColumn] === 'number' && typeof r[yColumn] === 'number')
    .slice(0, 150)
    .map((r) => ({ x: r[xColumn] as number, y: r[yColumn] as number }))

  const data = {
    datasets: [
      {
        label: `${yColumn} vs ${xColumn}`,
        data: pts,
        backgroundColor: '#FEB352',
        borderColor: '#B7E4F9',
        borderWidth: 1.5,
        pointRadius: 6,
      },
    ],
  }

  const options: ChartOptions<'scatter'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#F5EDE4' } },
      tooltip: BASE_TOOLTIP,
    },
    scales: {
      x: {
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR },
        title: { display: true, text: xColumn, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' } },
      },
      y: {
        grid: { color: GRID_COLOR },
        ticks: { color: TICK_COLOR },
        title: { display: true, text: yColumn, color: AXIS_TITLE_COLOR, font: { size: 11, weight: 'bold' } },
      },
    },
  }

  return (
    <div className="h-[280px] w-full">
      <Scatter data={data} options={options} />
    </div>
  )
}
