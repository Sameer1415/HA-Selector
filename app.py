import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, X } from "lucide-react";

const groupedData = {
  ORION: [
    {
      model: "Orion 1",
      image:
        "https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/orion-chargego/orion-charge-go_ric_black_1000x1000.jpg?rev=c993db8a8cb6470692b613a45f701c47&extension=webp&hash=5F307282D586208C92013BA20A652A59",
      price: 1000,
      summary: [
        "🔋 All-Day Rechargeable Power",
        "🎧 Crystal Clear Speech in Quiet",
        "🔊 Hear Voices Clearly in Noise",
        "🎨 Stylish, Modern Design",
        "💧 Sweat & Dust Resistant Build",
        "⚙️ Auto-Adjusting Smart Sound"
      ],
      features: {
        Bluetooth: true,
        Rechargeable: true,
        Waterproof: false,
        Channels: 16,
      },
    },
    {
      model: "Orion 2",
      price: 800,
      summary: [
        "🔋 All-Day Rechargeable Power",
        "🎧 Crystal Clear Speech in Quiet",
        "🔊 Hear Voices Clearly in Noise",
        "🎨 Stylish, Modern Design",
        "💧 Sweat & Dust Resistant Build",
        "⚙️ Auto-Adjusting Smart Sound"
      ],
      features: {
        Bluetooth: false,
        Rechargeable: true,
        Waterproof: false,
        Channels: 8,
      },
    },
  ],
  PURE: [
    {
      model: "Pure 1",
      price: 1500,
      features: {
        Bluetooth: true,
        Rechargeable: true,
        Waterproof: true,
        Channels: 20,
      },
    },
    {
      model: "Pure 2",
      price: 1200,
      features: {
        Bluetooth: true,
        Rechargeable: false,
        Waterproof: true,
        Channels: 12,
      },
    },
  ],
  SILK: [
    {
      model: "Silk 1",
      price: 900,
      features: {
        Bluetooth: false,
        Rechargeable: true,
        Waterproof: false,
        Channels: 6,
      },
    },
  ],
};

export default function ProductPage() {
  const [selectedGroup, setSelectedGroup] = useState(null);

  const renderFeatureIcon = (value) => {
    if (typeof value === "boolean") {
      return value ? <Check className="text-green-500" /> : <X className="text-red-500" />;
    }
    return value;
  };

  const renderComparisonTables = (products) => {
    const featureSet = Object.keys(products[0]?.features || {});
    const chunks = [];
    for (let i = 0; i < products.length; i += 4) {
      chunks.push(products.slice(i, i + 4));
    }

    return chunks.map((chunk, idx) => (
      <div key={idx} className="overflow-x-auto mt-6">
        <table className="min-w-full table-auto border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-left">Feature</th>
              {chunk.map((product) => (
                <th
                  key={product.model}
                  className="border border-gray-300 px-4 py-2 text-left"
                >
                  {product.model}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {featureSet.map((feature) => (
              <tr key={feature}>
                <td className="border border-gray-300 px-4 py-2">{feature}</td>
                {chunk.map((product) => (
                  <td key={product.model} className="border border-gray-300 px-4 py-2">
                    {renderFeatureIcon(product.features[feature])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    ));
  };

  const sortedGroups = selectedGroup
    ? [...groupedData[selectedGroup]].sort((a, b) => b.price - a.price)
    : [];

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-4">Titan HA Products</h1>
      <h2 className="text-2xl font-semibold mb-4">Select Model Group</h2>
      <div className="flex space-x-4 mb-6">
        {Object.keys(groupedData).map((group) => (
          <Button key={group} onClick={() => setSelectedGroup(group)}>
            {group}
          </Button>
        ))}
      </div>

      {selectedGroup && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedGroups.map((product, idx) => (
              <Card key={idx} className="w-full">
                <CardContent className="p-4">
                  <h3 className="text-xl font-semibold mb-2">{product.model}</h3>
                  {product.image && (
                    <img
                      src={product.image}
                      alt={product.model}
                      className="mb-4 h-48 object-contain mx-auto"
                    />
                  )}
                  {product.summary && (
                    <ul className="mb-4 text-sm list-disc list-inside text-gray-700">
                      {product.summary.map((line, i) => (
                        <li key={i}>{line}</li>
                      ))}
                    </ul>
                  )}
                  <ul className="text-sm">
                    {Object.entries(product.features).map(([key, value]) => (
                      <li key={key} className="flex items-center space-x-2">
                        <span className="font-medium w-28">{key}:</span>
                        {renderFeatureIcon(value)}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-12">
            {renderComparisonTables(sortedGroups)}
          </div>
        </>
      )}
    </div>
  );
}
