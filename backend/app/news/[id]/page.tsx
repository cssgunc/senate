export default function NewsArticlePage({ params }: { params: { id: string } }) {
  return (
    <main>
      <h1>News Article {params.id}</h1>
      <p>This page will display the full news article.</p>
    </main>
  );
}
