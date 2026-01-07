// Serve index.html para a rota raiz
export const onRequest: PagesFunction = async (context) => {
  // Simplesmente serve o index.html estático
  return context.env.ASSETS.fetch(context.request);
};
