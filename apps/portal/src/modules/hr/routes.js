import { BriefcaseBusiness, IdCard } from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)

export const routes = [
  { path: '/hr', name: 'hr-dashboard', component: page('HrPage'), meta: { title: 'Nhân sự', permission: 'hr.employees', documentTopbar: true } },
]

export const menu = {
  section: 'departments',
  label: 'Nhân sự',
  icon: IdCard,
  items: [
    { name: 'hr-dashboard', label: 'Tổng quan nhân sự', icon: BriefcaseBusiness },
  ],
}
