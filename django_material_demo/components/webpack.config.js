const path = require("path");

module.exports = async (env, options) => {
  const config = {
    devtool: "source-map",
    entry: {
      index: "./src/index.ts",
    },
    output: {
      path: path.join(__dirname, "/static/components/"),
      filename: "[name].js",
    },
    resolve: {
      extensions: [".ts", ".tsx", ".js"],
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: ["ts-loader"],
        },
      ],
    },
  };

  return config;
};
