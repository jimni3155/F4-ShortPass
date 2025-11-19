import {
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider,
} from 'react-router-dom';
import Start from '@pages/Start';
import CandidateInfo from '@pages/CandidateInfo';
import CandidateDone from '@pages/CandidateDone';
import AIInterview from '@pages/AIInterview';
import InterviewPage from '@pages/InterviewPage/InterviewPage';
import InterviewStart from '@pages/InterviewStart';
import CompanyInfo from '@pages/CompanyInfo';
import CompanyResult from '@pages/CompanyResult';
import Layout from '@layout/Layout';
import InterviewResult from '@pages/InterviewResult';
import CandidateListPage from '@pages/CandidateListPage';
import CandidateDetailPage from '@pages/CandidateDetailPage';

const App = () => {
  const router = createBrowserRouter(
    createRoutesFromElements(
      <Route path='/' element={<Layout />}>
        <Route index element={<Start />} />
        <Route path='/candidate/info' element={<CandidateInfo />} />
        <Route path='/candidate/start' element={<InterviewStart />} />
        <Route path='/candidate/interview' element={<InterviewPage />} />
        <Route path='/candidate/done' element={<CandidateDone />} />
        <Route path='/company/info' element={<CompanyInfo />} />
        <Route path='/company/result' element={<InterviewResult />} />
        <Route path='/company/applicants/:jobId' element={<CandidateListPage />} />
        <Route path='/company/applicants/:jobId/:applicantId' element={<CandidateDetailPage />} />
      </Route>
    )
  );
  return <RouterProvider router={router} />;
};

export default App;
