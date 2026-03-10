export default function CommitteePage({ params }: { params: { id: string } }) {
  return (
    <main>
      <h1>Committee {params.id}</h1>
      <p>This page will display information about Committee {params.id}.</p>
    </main>
  );
}
