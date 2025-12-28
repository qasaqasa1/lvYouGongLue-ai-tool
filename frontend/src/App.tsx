import { useState } from 'react';
import { LocationForm } from './components/LocationForm';
import { OutlineEditor } from './components/OutlineEditor';
import { OutlineNode } from './types';
import { Download, Edit3, ArrowLeft, Loader2 } from 'lucide-react';

function App() {
  const [step, setStep] = useState<'input' | 'outline' | 'generating' | 'done'>('input');
  const [location, setLocation] = useState('');
  const [outline, setOutline] = useState<OutlineNode[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const handleGenerateOutline = async (loc: string, days?: number, budget?: string) => {
    setIsLoading(true);
    setLocation(loc);
    try {
      const response = await fetch('http://localhost:8000/api/generate-outline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location: loc, days, budget }),
      });
      
      if (!response.ok) throw new Error('Failed to generate outline');
      
      const data = await response.json();
      setOutline(data.outline);
      setStep('outline');
    } catch (error) {
      console.error(error);
      alert('生成大纲失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateContent = async () => {
    setIsLoading(true);
    setStep('generating');
    try {
      const response = await fetch('http://localhost:8000/api/generate-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, outline }),
      });

      if (!response.ok) throw new Error('Failed to generate content');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
      setStep('done');
    } catch (error) {
      console.error(error);
      alert('生成内容失败，请重试');
      setStep('outline');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
            AI 旅游攻略生成器
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            一键生成专业旅游攻略，支持大纲编辑与多文档导出
          </p>
        </header>

        <main>
          {step === 'input' && (
            <LocationForm onSubmit={handleGenerateOutline} isLoading={isLoading} />
          )}

          {step === 'outline' && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <button 
                  onClick={() => setStep('input')}
                  className="flex items-center text-gray-500 hover:text-gray-700"
                >
                  <ArrowLeft size={20} className="mr-1" /> 重选地点
                </button>
                <h2 className="text-2xl font-bold text-center flex-1 pr-20">
                  {location} - 攻略大纲
                </h2>
              </div>
              
              <div className="mb-8">
                <p className="text-sm text-gray-500 mb-4 bg-blue-50 p-3 rounded-lg border border-blue-100">
                  💡 提示：您可以点击标题进行修改，使用右侧按钮添加/删除节点，或者拖拽调整顺序（开发中）。
                  确认无误后点击下方按钮生成完整文档。
                </p>
                <OutlineEditor nodes={outline} onChange={setOutline} />
              </div>

              <div className="flex justify-end pt-6 border-t">
                <button
                  onClick={handleGenerateContent}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 shadow-lg transition"
                >
                  {isLoading ? (
                    <><Loader2 className="animate-spin" /> 生成中...</>
                  ) : (
                    <><Edit3 size={20} /> 确认大纲并生成文章</>
                  )}
                </button>
              </div>
            </div>
          )}

          {step === 'generating' && (
            <div className="text-center py-20 bg-white rounded-xl shadow-lg">
              <Loader2 className="animate-spin w-16 h-16 text-blue-600 mx-auto mb-6" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">正在疯狂码字中...</h3>
              <p className="text-gray-500">AI 正在为您撰写关于 {location} 的详细攻略，请稍候</p>
            </div>
          )}

          {step === 'done' && (
            <div className="text-center py-16 bg-white rounded-xl shadow-lg">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Download className="w-10 h-10 text-green-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">生成完成！</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                您的攻略文档已准备就绪。包含了 {outline.filter(n => n.level === 1).length} 篇独立文章。
              </p>
              
              <div className="flex justify-center gap-4">
                <button 
                   onClick={() => setStep('outline')}
                   className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                  返回编辑
                </button>
                {downloadUrl && (
                  <a
                    href={downloadUrl}
                    download={`${location}_guide.zip`}
                    className="flex items-center gap-2 px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 shadow-lg transition"
                  >
                    <Download size={20} /> 下载全部文档 (ZIP)
                  </a>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
