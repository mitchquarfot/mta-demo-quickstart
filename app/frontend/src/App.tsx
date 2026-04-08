import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Attribution from "./pages/Attribution";
import ChannelPerformance from "./pages/ChannelPerformance";
import ConversionPaths from "./pages/ConversionPaths";
import Incrementality from "./pages/Incrementality";
import UnifiedMeasurement from "./pages/UnifiedMeasurement";
import CampaignExplorer from "./pages/CampaignExplorer";
import CampaignPlanner from "./pages/CampaignPlanner";
import AskCortex from "./pages/AskCortex";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/attribution" element={<Attribution />} />
        <Route path="/channels" element={<ChannelPerformance />} />
        <Route path="/paths" element={<ConversionPaths />} />
        <Route path="/incrementality" element={<Incrementality />} />
        <Route path="/unified" element={<UnifiedMeasurement />} />
        <Route path="/campaigns" element={<CampaignExplorer />} />
        <Route path="/planner" element={<CampaignPlanner />} />
        <Route path="/ask" element={<AskCortex />} />
      </Routes>
    </Layout>
  );
}
