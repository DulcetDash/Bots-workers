const { image_search } = require("duckduckgo-images-api");

(async () => {
  const results = await image_search({
    query: "Sensai Ultimate Concentrate",
    moderate: true,
  });

  console.log(results[0]);
})();
