import { Navigate, Route, Routes } from 'react-router-dom';

import { LandingPage } from '@/ui/overlays/LandingPage';
import { QuickPortfolioPage } from '@/ui/quick-portfolio/QuickPortfolioPage';
import { ResumePage } from '@/ui/overlays/ResumePage';
import { ContactPage } from '@/ui/overlays/ContactPage';
import { ExperienceRoute } from '@/app/routes/ExperienceRoute';
import { APP_ROUTE_PATHS } from '@/navigation/routes/appRoutes';

export function AppRoutes() {
  return (
    <Routes>
      <Route path={APP_ROUTE_PATHS.landing} element={<LandingPage />} />
      <Route path={APP_ROUTE_PATHS.experience} element={<ExperienceRoute />} />
      <Route path={APP_ROUTE_PATHS.experienceRoom} element={<ExperienceRoute />} />
      <Route path={APP_ROUTE_PATHS.portfolio} element={<QuickPortfolioPage />} />
      <Route
        path={APP_ROUTE_PATHS.portfolioAbout}
        element={<QuickPortfolioPage section="about" />}
      />
      <Route
        path={APP_ROUTE_PATHS.portfolioExperience}
        element={<QuickPortfolioPage section="experience" />}
      />
      <Route
        path={APP_ROUTE_PATHS.portfolioSkills}
        element={<QuickPortfolioPage section="skills" />}
      />
      <Route
        path={APP_ROUTE_PATHS.portfolioProjects}
        element={<QuickPortfolioPage section="projects" />}
      />
      <Route
        path={APP_ROUTE_PATHS.portfolioProject}
        element={<QuickPortfolioPage section="projects" />}
      />
      <Route
        path={APP_ROUTE_PATHS.portfolioArchitecture}
        element={<QuickPortfolioPage section="architecture" />}
      />
      <Route path={APP_ROUTE_PATHS.resume} element={<ResumePage />} />
      <Route path={APP_ROUTE_PATHS.contact} element={<ContactPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
