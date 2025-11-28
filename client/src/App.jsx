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
import CompanyResult from '@pages/CompanyResult';
import Layout from '@layout/Layout';
import InterviewResult from '@pages/InterviewResult';
import CandidateListPage from '@pages/CandidateListPage';
import CandidateDetailPage from '@pages/CandidateDetailPage';
import PersonaGeneration from '@pages/PersonaGeneration';
import CandidateJobs from '@pages/CandidateJobs';
import InterviewPrepare from '@pages/InterviewPrepare';
import EvaluationPage from '@pages/EvaluationPage';
import CandidateEvaluation from '@pages/CandidateEvaluation';
import AgentLogs from '@pages/AgentLogs';

const App = () => {
  const router = createBrowserRouter(
    createRoutesFromElements(
      <Route path='/' element={<Layout />}>
        <Route index element={<Start />} />
        <Route path='/candidate/info' element={<CandidateInfo />} />
        <Route path='/candidate/jobs' element={<CandidateJobs />} />
        <Route path='/candidate/start' element={<InterviewPrepare />} />
        <Route path='/candidate/interview' element={<InterviewPage />} />
        <Route path='/candidate/done' element={<CandidateDone />} />
        <Route path='/company/info' element={<PersonaGeneration />} />
        <Route path='/company/result' element={<InterviewResult />} />
        <Route
          path='/company/applicant/:id'
          element={<CandidateEvaluation />}
        />
        <Route path='/company/applicants/:jobId' element={<CandidateListPage />} />
        <Route path='/company/applicants/:jobId/:applicantId' element={<CandidateDetailPage />} />
        <Route path='/evaluation/:interviewId' element={<EvaluationPage />} />
        <Route path='/agent-logs' element={<AgentLogs />} />
        <Route path='/agent-logs/:evaluationId' element={<AgentLogs />} />
      </Route>
    )
  );
  return <RouterProvider router={router} />;
};

export default App;
