// lightweight senator detail stub

export default async function SenatorStubPage(props: any) {
  const { params } = props as any;
  const { id } = params ?? { id: "unknown" };
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">Senator {id}</h1>
      <p className="text-sm text-muted-foreground">
        This is a placeholder page for senator {id}.
      </p>
    </div>
  );
}
