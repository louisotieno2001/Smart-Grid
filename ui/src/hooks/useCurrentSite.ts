import { useParams } from "react-router-dom";

export function useCurrentSite() {
  const { siteId } = useParams();
  return siteId || null;
}
