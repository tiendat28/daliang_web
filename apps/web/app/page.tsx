import type { Metadata } from "next";
import LandingHeader from "@/components/dlvc/landing/LandingHeader";
import Hero from "@/components/dlvc/landing/Hero";
import AboutSection from "@/components/dlvc/landing/AboutSection";
import ProductsSection from "@/components/dlvc/landing/ProductsSection";
import ServicesSection from "@/components/dlvc/landing/ServicesSection";
import TrustSection from "@/components/dlvc/landing/TrustSection";
import ContactSection from "@/components/dlvc/landing/ContactSection";
import LandingFooter from "@/components/dlvc/landing/LandingFooter";

export const metadata: Metadata = {
  title: "Daliang VN – Hoá chất xử lý bề mặt kim loại",
  description:
    "Công ty TNHH Hóa chất Daliang VN cung cấp hoá chất tiền xử lý, phụ gia mạ và dung dịch thụ động cho các nhà máy xi mạ công nghiệp tại Việt Nam.",
};

export default function HomePage() {
  return (
    <div className="bg-dlvc-paper text-dlvc-landing-ink">
      <LandingHeader />
      <Hero />
      <AboutSection />
      <ProductsSection />
      <ServicesSection />
      <TrustSection />
      <ContactSection />
      <LandingFooter />
    </div>
  );
}
