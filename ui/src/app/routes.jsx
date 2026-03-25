import PortfolioPage from "../features/portfolio/PortfolioPage";
import FacilitiesPage from "../features/facilities/FacilitiesPage";
import RecsPage from "../features/recommendations/RecsPage";
import AlertsPage from "../features/alerts/AlertsPage";
import IntakePage from "../features/intake/IntakePage";
import ROIPage from "../features/roi/ROIPage";
import APIPage from "../features/api/APIPage";
import PartnerDashboardPage from "../features/partners/PartnerDashboardPage";

export const PAGE_COMPONENTS = {
  portfolio: { component: PortfolioPage, title: "Portfolio overview", breadcrumb: "ArcelorGroup" },
  facilities: { component: FacilitiesPage, title: "Facilities", breadcrumb: "ArcelorGroup / Facilities" },
  recs: { component: RecsPage, title: "Recommendations", breadcrumb: "Steelworks A / Recommendations" },
  alerts: { component: AlertsPage, title: "Alerts & monitoring", breadcrumb: "Platform" },
  intake: { component: IntakePage, title: "Data intake", breadcrumb: "Onboarding" },
  roi: { component: ROIPage, title: "ROI calculator", breadcrumb: "Sales tools" },
  api: { component: APIPage, title: "API explorer", breadcrumb: "Developer" },
  partners: { component: PartnerDashboardPage, title: "Partner integrations", breadcrumb: "Third-party partners" },
};
