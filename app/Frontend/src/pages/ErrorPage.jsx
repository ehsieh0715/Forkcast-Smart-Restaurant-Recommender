import { useRouteError } from "react-router-dom";

export default function ErrorPage() {
  const error = useRouteError();

  let title = "Something went wrong";
  let message = "An unexpected error has occurred.";

  console.error("❌ Route error:", error);

  if (error.status === 500) {
    message = error.data?.message || "Internal Server Error.";
  } else if (error.status === 404) {
    title = "404 - Page Not Found";
    message = "The page you’re looking for doesn’t exist or has been moved.";
  }

  return (
    <main className="flex h-screen flex-col items-center justify-center bg-gray-50 px-6 text-center text-gray-700">
      <img
        src="/page-not-found.svg"
        alt="Error illustration"
        className="mb-8 w-full max-w-xs md:max-w-sm"
      />
      <h1 className="text-3xl font-bold text-indigo-600 md:text-4xl">
        {title}
      </h1>
      <p className="mt-3 max-w-md text-sm text-gray-500 md:text-base">
        {message}
      </p>
      <a
        href="/"
        className="mt-6 inline-block rounded-md bg-indigo-600 px-5 py-2 text-white shadow transition hover:bg-indigo-700"
      >
        Go back home
      </a>
    </main>
  );
}
