<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="px-6 py-4 shadow bg-white">
      <nav class="flex items-center gap-4">
        <a href="/" class="font-semibold">Loksewa Quiz Hub</a>
        <a href="/quiz">Quiz</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/admin">Admin</a>
      </nav>
    </header>
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>
