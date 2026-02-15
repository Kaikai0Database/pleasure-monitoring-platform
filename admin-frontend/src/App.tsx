import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Watchlist from './pages/Watchlist';
import PatientDetail from './pages/PatientDetail';
import PatientAssignments from './pages/PatientAssignments';
import NurseDetail from './pages/NurseDetail';
import Layout from './components/Layout';
import './App.css';

function App() {
  const isAuthenticated = () => {
    return !!localStorage.getItem('admin_token');
  };

  const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    return isAuthenticated() ? <>{children}</> : <Navigate to="/" />;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/watchlist"
          element={
            <PrivateRoute>
              <Layout>
                <Watchlist />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/assignments"
          element={
            <PrivateRoute>
              <Layout>
                <PatientAssignments />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/nurse/:nurseId"
          element={
            <PrivateRoute>
              <Layout>
                <NurseDetail />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/patient/:id"
          element={
            <PrivateRoute>
              <Layout>
                <PatientDetail />
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
