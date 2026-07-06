import type { JSX } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import AdminRoute from "./components/AdminRoute";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Admin from "./pages/Admin";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import JobDetails from "./pages/JobDetails";
import Jobs from "./pages/Jobs";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Recommendations from "./pages/Recommendations";
import Register from "./pages/Register";
import ResumeUpload from "./pages/ResumeUpload";
import SavedJobs from "./pages/SavedJobs";
import SkillGap from "./pages/SkillGap";

function withLayout(node: JSX.Element) {
  return (
    <ProtectedRoute>
      <Layout>{node}</Layout>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/dashboard" element={withLayout(<Dashboard />)} />
      <Route path="/profile" element={withLayout(<Profile />)} />
      <Route path="/resume" element={withLayout(<ResumeUpload />)} />
      <Route path="/jobs" element={withLayout(<Jobs />)} />
      <Route path="/jobs/:id" element={withLayout(<JobDetails />)} />
      <Route path="/recommendations" element={withLayout(<Recommendations />)} />
      <Route path="/saved" element={withLayout(<SavedJobs />)} />
      <Route path="/history" element={withLayout(<History />)} />
      <Route path="/skill-gap/:jobId" element={withLayout(<SkillGap />)} />

      <Route
        path="/admin"
        element={
          <AdminRoute>
            <Layout>
              <Admin />
            </Layout>
          </AdminRoute>
        }
      />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
