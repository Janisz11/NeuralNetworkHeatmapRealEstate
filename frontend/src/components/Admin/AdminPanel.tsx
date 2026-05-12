

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { getModels, getMe } from "../../api/client";
import type { ModelRun, User } from "../../types";
import { ModelRunsTable } from "./ModelRunsTable";

export function AdminPanel() {
  const [searchParams] = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [models, setModels] = useState<ModelRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
   
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("auth_token", token);
      window.history.replaceState({}, "", "/admin"); 
    }

    getMe()
      .then(setUser)
      .catch(() => setError("Nie jesteś zalogowany. Kliknij poniżej, aby zalogować się przez Google."));

    getModels().then(setModels).catch(() => {});
  }, [searchParams]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-gray-400">{error}</p>
          <a
            href="/auth/google"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors"
          >
            Zaloguj przez Google
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Panel administracyjny</h1>
          <p className="text-gray-400 text-sm">NeuralMap Wrocław</p>
        </div>
        {user && (
          <div className="flex items-center gap-3">
            {user.picture && (
              <img src={user.picture} alt="avatar" className="w-9 h-9 rounded-full" />
            )}
            <div>
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-gray-400">{user.email}</p>
            </div>
            <button
              onClick={() => { localStorage.removeItem("auth_token"); window.location.reload(); }}
              className="text-xs text-gray-500 hover:text-red-400 transition-colors ml-2"
            >
              Wyloguj
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-blue-400">{models.length}</p>
          <p className="text-sm text-gray-400 mt-1">Modeli łącznie</p>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-green-400">
            {models.filter((m) => m.status === "done").length}
          </p>
          <p className="text-sm text-gray-400 mt-1">Ukończonych</p>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-yellow-400">
            {models.filter((m) => m.status === "training").length}
          </p>
          <p className="text-sm text-gray-400 mt-1">W trakcie</p>
        </div>
      </div>

      <ModelRunsTable models={models} />
    </div>
  );
}
