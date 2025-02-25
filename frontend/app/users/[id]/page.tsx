"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchUser } from "../../../services/api";
import { FaStickyNote, FaEnvelope, FaPhoneAlt, FaCalendarAlt } from "react-icons/fa";

export default function InnersenseMockup() {
  const [selectedTab, setSelectedTab] = useState("activities");
  const { id } = useParams();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    try {
      const data = await fetchUser(id);
      setUser(data);
    } catch (error) {
      console.error("Error loading users:", error);
    }
  }
  if (!user) return <p>Loading...</p>;

  return (
    <div className="flex h-screen bg-gray-50 text-sm">
      <div className="flex flex-1 flex-col">
        <div className="flex flex-1">
          {/* Record Detail Section */}
          <section className="w-64 bg-gray-100 p-4 space-y-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold">{user.name}</h3>
            <p>Amount: <span className="font-bold">$218,400</span></p>
            <p>Close Date: <span className="font-bold">Feb 14, 2025</span></p>
            <p>Stage: <span className="text-blue-400">Contracting</span></p>
            <p>Pipeline: <span className="text-blue-400">Encoda 2025 Pipeline</span></p>
            
            {/* Centered Small Circle Icon Buttons with Labels */}
            <div className="flex justify-center space-x-3 mt-3">
              <div className="flex flex-col items-center">
                <button className="p-2 bg-gray-300 rounded-full hover:bg-gray-400 transition duration-200">
                  <FaStickyNote className="text-gray-700 text-sm" />
                </button>
                <span className="text-xs text-gray-600 mt-1">Note</span>
              </div>
              <div className="flex flex-col items-center">
                <button className="p-2 bg-gray-300 rounded-full hover:bg-gray-400 transition duration-200">
                  <FaEnvelope className="text-gray-700 text-sm" />
                </button>
                <span className="text-xs text-gray-600 mt-1">Email</span>
              </div>
              <div className="flex flex-col items-center">
                <button className="p-2 bg-gray-300 rounded-full hover:bg-gray-400 transition duration-200">
                  <FaPhoneAlt className="text-gray-700 text-sm" />
                </button>
                <span className="text-xs text-gray-600 mt-1">Call</span>
              </div>
              <div className="flex flex-col items-center">
                <button className="p-2 bg-gray-300 rounded-full hover:bg-gray-400 transition duration-200">
                  <FaCalendarAlt className="text-gray-700 text-sm" />
                </button>
                <span className="text-xs text-gray-600 mt-1">Meeting</span>
              </div>
            </div>
          </section>

          {/* Main Content */}
          <main className="flex-1 flex flex-col">
            {/* Secondary Navigation */}
            <div className="flex border-b bg-white shadow-md p-3 space-x-5">
              <button 
                className={`px-3 py-1 border-b-4 ${selectedTab === "overview" ? "border-blue-500 text-blue-500 font-semibold" : "border-transparent text-gray-600"}`} 
                onClick={() => setSelectedTab("overview")}
              >
                Overview
              </button>
              <button 
                className={`px-3 py-1 border-b-4 ${selectedTab === "activities" ? "border-blue-500 text-blue-500 font-semibold" : "border-transparent text-gray-600"}`} 
                onClick={() => setSelectedTab("activities")}
              >
                Activities
              </button>
              <button 
                className={`px-3 py-1 border-b-4 ${selectedTab === "roi" ? "border-blue-500 text-blue-500 font-semibold" : "border-transparent text-gray-600"}`} 
                onClick={() => setSelectedTab("roi")}
              >
                ROI Calc
              </button>
            </div>

            {/* Activity Section */}
            {selectedTab === "activities" && (
              <section className="mt-3 bg-white p-3 rounded shadow-md-lg">
                <h2 className="text-md font-semibold">Activity</h2>
                <div className="mt-3">
                  <div className="bg-white p-6 shadow-lg rounded-lg">
                    <h2 className="text-xl font-bold text-gray-800">{user.name}</h2>
                    <p className="text-gray-600">Email: {user.email}</p>
                    <p className="text-gray-600">Phone: {user.phone}</p>
                  </div>
                  <div className="p-4 border rounded-lg shadow-sm mb-3">
                    <p className="font-bold">📌 Note by Sherry Grimaldi</p>
                    <p className="text-gray-600">Notes from Tiffany Turk for Demo on 11/8 at 11am EST.</p>
                  </div>
                  <div className="p-4 border rounded-lg shadow-sm mb-3">
                    <p className="font-bold">📅 Meeting - Copa Health & Encoda</p>
                    <p className="text-gray-600">Hosted by Sam Ambrose</p>
                  </div>
                  <div className="p-3 border rounded">
                    <p className="font-bold">📧 Email - RE: Encoda Meeting Request</p>
                    <p className="text-gray-600">Yes. I’ll send you both an invite. Thanks.</p>
                  </div>
                </div>
              </section>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
