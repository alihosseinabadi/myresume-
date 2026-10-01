import TopBar from '@/components/shell/TopBar'
import SiteFooter from '@/components/shell/SiteFooter'
import Hero from '@/components/hero/Hero'
import Marquee from '@/components/sections/Marquee'
import Studio from '@/components/studio/Studio'
import Toolkit from '@/components/sections/Toolkit'
import TemplateRail from '@/components/sections/TemplateRail'
import PricingTiers from '@/components/sections/PricingTiers'
import FaqShort from '@/components/sections/FaqShort'
import StructuredData from '@/components/shared/StructuredData'

export default function Home() {
  return (
    <>
      <TopBar />
      <main>
        <Hero />
        <Marquee />
        <section className="shell py-16 md:py-20">
          <Studio />
        </section>
        <Toolkit />
        <TemplateRail />
        <PricingTiers />
        <FaqShort />
      </main>
      <SiteFooter />
      <StructuredData />
    </>
  )
}
