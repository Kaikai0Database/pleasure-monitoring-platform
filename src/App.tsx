import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { ProfileSetup } from './pages/ProfileSetup';
import { GameMenu } from './pages/GameMenu';
import { GameAssessment } from './pages/GameAssessment';
import { GameResult } from './pages/GameResult';
import { ScoreHistory } from './pages/ScoreHistory';
import { DiaryCalendar } from './pages/DiaryCalendar';
import { DiaryEditor } from './pages/DiaryEditor';

import { FontSizeProvider } from './context/FontSizeContext';
import { BackgroundMusic } from './components/BackgroundMusic';
import { Settings } from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <FontSizeProvider>
        <BackgroundMusic>
          <BrowserRouter>
            <Routes>
              {/* Routes with Layout (header and padding) */}
              <Route element={<Layout />}>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/profile-setup" element={<ProfileSetup />} />
                <Route path="/" element={<GameMenu />} />
                <Route path="/history" element={<ScoreHistory />} />
                <Route path="/diary" element={<DiaryCalendar />} />
                <Route path="/diary/new" element={<DiaryEditor />} />
                <Route path="/diary/edit/:id" element={<DiaryEditor />} />
                <Route path="/settings" element={<Settings />} />
              </Route>

              {/* Fullscreen routes without Layout */}
              <Route path="/game/assessment" element={<GameAssessment />} />
              <Route path="/game/result" element={<GameResult />} />
            </Routes>
          </BrowserRouter>
        </BackgroundMusic>
      </FontSizeProvider>
    </AuthProvider>
  );
}

export default App;
