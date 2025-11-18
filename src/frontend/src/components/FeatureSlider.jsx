// src/frontend/src/components/FeatureSlider.jsx
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import { Search, BrainCircuit, GitPullRequest, LineChart } from 'lucide-react';

const features = [
  { 
    title: "Causal Discovery", 
    desc: "Uses the PC Algorithm to infer cause-and-effect directionality from observational data.",
    color: "bg-blue-500/10 border-blue-500/20", 
    iconColor: "text-blue-400",
    icon: <Search size={40} /> 
  },
  { 
    title: "Neural SCM", 
    desc: "Fits Structural Causal Models using PyTorch neural networks to learn non-linear equations.",
    color: "bg-purple-500/10 border-purple-500/20", 
    iconColor: "text-purple-400",
    icon: <BrainCircuit size={40} /> 
  },
  { 
    title: "Counterfactuals", 
    desc: "Replays history. Infers specific noise of past events to simulate alternate realities accurately.",
    color: "bg-pink-500/10 border-pink-500/20", 
    iconColor: "text-pink-400",
    icon: <GitPullRequest size={40} /> 
  },
  { 
    title: "Monte Carlo Sim", 
    desc: "Runs 1,000+ future simulations to estimate the net impact of policy changes.",
    color: "bg-emerald-500/10 border-emerald-500/20", 
    iconColor: "text-emerald-400",
    icon: <LineChart size={40} /> 
  },
];

export default function FeatureSlider() {
  return (
    <div className="py-8 px-4 w-full">
      <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white">
              Core <span className="text-brand-500">Capabilities</span>
          </h2>
      </div>
      
      {/* CRITICAL FIX: 
         slidesPerView={1} forces one card.
         centeredSlides={true} ensures it sits in the middle.
      */}
      <Swiper
        modules={[Navigation, Pagination, Autoplay]}
        spaceBetween={40}
        slidesPerView={1}
        centeredSlides={true}
        autoplay={{ delay: 3000, disableOnInteraction: false }}
        navigation
        pagination={{ clickable: true }}
        className="pb-16 !px-2 w-full"
      >
        {features.map((f, i) => (
          <SwiperSlide key={i}>
            <div className={`h-full min-h-[350px] rounded-[2.5rem] p-10 border ${f.color} bg-white dark:bg-[#0f0f0f] shadow-xl dark:shadow-none flex flex-col items-center text-center justify-center transition-all hover:-translate-y-2`}>
              <div className={`w-20 h-20 rounded-full bg-white/5 flex items-center justify-center shadow-lg mb-6 ${f.iconColor}`}>
                {f.icon}
              </div>
              <h3 className="text-3xl font-bold mb-4 text-white">{f.title}</h3>
              <p className="text-lg text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}