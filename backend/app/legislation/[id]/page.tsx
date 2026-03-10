export default function LegislationPage({ params }: { params: { id: string } }) {
  return (
    <main>
      <h1>Legislation {params.id}</h1>
      <p>This page will display information about Legislation {params.id}.</p>
    </main>
  );
}