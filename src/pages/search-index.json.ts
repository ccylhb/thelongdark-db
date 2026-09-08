import food from "../data/thelongdark_food.json";
import clothing from "../data/thelongdark_clothing.json";
import tools from "../data/thelongdark_tools.json";
import firstaid from "../data/thelongdark_firstaid.json";
import aff from "../data/thelongdark_afflictions.json";

export function GET() {
  const entries = [
    ...food.map((x: any) => ({
      title: x.title,
      href: `/food/${x.slug}/`,
      sub: `Food · ${x.fields?.calories || "?"} kcal · ${x.fields?.weight || "?"} kg`,
      icon: x.icon_file || "",
    })),
    ...clothing.map((x: any) => ({
      title: x.title,
      href: `/clothing/${x.slug}/`,
      sub: `Clothing · ${x.fields?.["warmth bonus"] || "?"}°C warmth${x.fields?.["clothing slot"] ? ` · ${x.fields?.["clothing slot"]}` : ""}`,
      icon: x.icon_file || "",
    })),
    ...tools.map((x: any) => ({
      title: x.title,
      href: `/tools/${x.slug}/`,
      sub: `Tool · ${x.fields?.weight || "?"} kg`,
      icon: x.icon_file || "",
    })),
    ...firstaid.map((x: any) => ({
      title: x.title,
      href: `/firstaid/${x.slug}/`,
      sub: `First aid · ${x.fields?.weight || "?"} kg`,
      icon: x.icon_file || "",
    })),
    ...aff.map((x: any) => ({
      title: x.title,
      href: `/afflictions/${x.slug}/`,
      sub: `Affliction · ${x.fields?.["type (benefit/injury/disease)"] || ""}`,
      icon: x.icon_file || "",
    })),
  ].sort((a, b) => a.title.localeCompare(b.title));
  return new Response(JSON.stringify(entries), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
