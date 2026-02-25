import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { User } from '../types/api';
import { PixelCard } from '../components/ui/PixelCard';
import { PixelButton } from '../components/ui/PixelButton';
import { PixelInput } from '../components/ui/PixelInput';


export const ProfileSetup: React.FC = () => {
    const { user, updateProfile } = useAuth();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [step, setStep] = useState(1);

    // Redirect if already completed
    React.useEffect(() => {
        if (user?.is_profile_completed) {
            navigate('/');
        }
    }, [user, navigate]);

    // Form State
    const [formData, setFormData] = useState({
        nickname: user?.nickname || '',
        dob: user?.dob || '',
        gender: user?.gender || '', // 'male', 'female', 'non-binary'
        height: user?.height || 160,
        weight: user?.weight || 60,
        education: user?.education || '',
        marital_status: user?.marital_status || '',
        marriage_other: user?.marriage_other || '',
        has_children: user?.has_children !== undefined ? user.has_children : null,
        children_count: user?.children_count || 0,
        economic_status: user?.economic_status || '',
        family_structure: user?.family_structure || '',
        family_other: user?.family_other || '',
        has_job: user?.has_job !== undefined ? user.has_job : null,
        salary_range: user?.salary_range || '',
        location_city: user?.location_city || '', // Keep simple for demo, or real address picker? "Slide to choose" implies select
        location_district: user?.location_district || '',
        living_situation: user?.living_situation || '',
        cohabitant_count: user?.cohabitant_count || 0,
        religion: user?.religion !== undefined ? user.religion : null,
        religion_other: user?.religion_other || '',
        group: user?.group === 'student' ? '學校' : user?.group === 'clinical' ? '醫院' : ''
    });

    const handleChange = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async () => {
        setIsLoading(true);
        try {
            // Prepare profile data with proper type conversion
            // Convert null to undefined for optional boolean fields to match User interface
            const profileData: Partial<User> = {
                ...formData,
                height: parseFloat(formData.height as any),
                weight: parseFloat(formData.weight as any),
                has_children: formData.has_children === null ? undefined : formData.has_children,
                has_job: formData.has_job === null ? undefined : formData.has_job,
                religion: formData.religion === null ? undefined : formData.religion,
                group: formData.group === '學校' ? 'student' : formData.group === '醫院' ? 'clinical' : formData.group
            };

            console.log('📤 Submitting profile data:', profileData);

            // Use updateProfile from AuthContext which properly updates both state and localStorage
            await updateProfile(profileData);

            console.log('✅ Profile updated successfully');

            // Navigate to home page - Layout won't redirect back because user state is now updated
            navigate('/');
        } catch (err: any) {
            console.error('❌ Profile update error:', err);
            alert(err.message || '更新失敗，請稍後再試');
        } finally {
            setIsLoading(false);
        }
    };

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    // Validation functions for each step
    const isStep1Valid = () => {
        const dobParts = formData.dob ? formData.dob.split('-') : ['', '', ''];
        const yearValid = dobParts[0] && dobParts[0].length === 4;
        const monthValid = dobParts[1] && dobParts[1].length >= 1 && dobParts[1].length <= 2;
        const dayValid = dobParts[2] && dobParts[2].length >= 1 && dobParts[2].length <= 2;
        return formData.nickname.trim() !== '' &&
            yearValid && monthValid && dayValid &&
            formData.gender !== '' &&
            formData.group !== '';
    };

    const isStep2Valid = () => {
        return formData.height > 0 && formData.weight > 0;
    };

    const isStep3Valid = () => {
        const baseValid = formData.education !== '' &&
            formData.has_job !== null &&
            formData.economic_status !== '';
        const jobValid = formData.has_job === false || (formData.has_job === true && formData.salary_range !== '');
        return baseValid && jobValid;
    };

    const isStep4Valid = () => {
        const maritalValid = formData.marital_status !== '' &&
            (formData.marital_status !== '其他' || formData.marriage_other.trim() !== '');
        const childrenValid = formData.has_children !== null &&
            (formData.has_children === false || formData.children_count > 0);
        const familyValid = formData.family_structure !== '' &&
            (formData.family_structure !== '其他' || formData.family_other.trim() !== '');
        const livingValid = formData.living_situation !== '' &&
            (formData.living_situation === '獨居' || formData.cohabitant_count > 0);
        const locationValid = formData.location_city.trim() !== '' && formData.location_district.trim() !== '';
        const religionValid = formData.religion !== null &&
            (formData.religion === false || formData.religion_other.trim() !== '');
        return maritalValid && childrenValid && familyValid && livingValid && locationValid && religionValid;
    };

    const canProceed = () => {
        switch (step) {
            case 1: return isStep1Valid();
            case 2: return isStep2Valid();
            case 3: return isStep3Valid();
            case 4: return isStep4Valid();
            default: return false;
        }
    };

    // Render Helpers (simplified styling)
    const Label = ({ children }: { children: React.ReactNode }) => <label className="block text-lg font-bold mb-2">{children}</label>;

    // Step 1: Basic Info (Nickname, DOB, Gender)
    const renderStep1 = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold mb-4">基本資料 (1/4)</h3>
            <div>
                <Label>暱稱</Label>
                <PixelInput
                    value={formData.nickname}
                    onChange={e => handleChange('nickname', e.target.value)}
                    placeholder="請輸入暱稱"
                />
            </div>
            <div>
                <Label>出生年月日</Label>
                <div style={{
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: 'center',
                    gap: '4px',
                    width: '100%',
                    overflow: 'hidden',
                }}>
                    <input
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={4}
                        className="p-2 border-4 border-black font-pixel text-lg text-center"
                        style={{ flex: 2, minWidth: 0 }}
                        value={formData.dob ? formData.dob.split('-')[0] : ''}
                        onChange={e => {
                            const year = e.target.value.replace(/\D/g, '').slice(0, 4);
                            const parts = formData.dob ? formData.dob.split('-') : ['', '', ''];
                            parts[0] = year;
                            handleChange('dob', parts.join('-'));
                        }}
                        placeholder="年"
                    />
                    <span className="text-xl font-bold" style={{ flexShrink: 0 }}>年</span>
                    <input
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={2}
                        className="p-2 border-4 border-black font-pixel text-lg text-center"
                        style={{ flex: 1, minWidth: 0 }}
                        value={formData.dob ? formData.dob.split('-')[1] : ''}
                        onChange={e => {
                            const month = e.target.value.replace(/\D/g, '').slice(0, 2);
                            const parts = formData.dob ? formData.dob.split('-') : ['', '', ''];
                            parts[1] = month;
                            handleChange('dob', parts.join('-'));
                        }}
                        placeholder="月"
                    />
                    <span className="text-xl font-bold" style={{ flexShrink: 0 }}>月</span>
                    <input
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={2}
                        className="p-2 border-4 border-black font-pixel text-lg text-center"
                        style={{ flex: 1, minWidth: 0 }}
                        value={formData.dob ? formData.dob.split('-')[2] : ''}
                        onChange={e => {
                            const day = e.target.value.replace(/\D/g, '').slice(0, 2);
                            const parts = formData.dob ? formData.dob.split('-') : ['', '', ''];
                            parts[2] = day;
                            handleChange('dob', parts.join('-'));
                        }}
                        placeholder="日"
                    />
                    <span className="text-xl font-bold" style={{ flexShrink: 0 }}>日</span>
                </div>
            </div>
            <div>
                <Label>性別</Label>
                <div className="flex gap-4">
                    {['生理男', '生理女', '非二元性別'].map(opt => (
                        <button
                            key={opt}
                            className={`flex-1 py-3 border-4 border-black font-bold ${formData.gender === opt ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                            onClick={() => handleChange('gender', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            </div>
            <div>
                <Label>您來自哪裡?</Label>
                <div className="flex gap-4">
                    {['學校', '醫院'].map(opt => (
                        <button
                            key={opt}
                            className={`flex-1 py-3 border-4 border-black font-bold ${formData.group === opt ? 'bg-black text-white' : 'bg-white hover:bg-gray-100'}`}
                            onClick={() => handleChange('group', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );

    // Step 2: Body (Height, Weight) - Using Range Sliders
    const renderStep2 = () => (
        <div className="space-y-8">
            <h3 className="text-2xl font-bold mb-4">身體數值 (2/4)</h3>
            <div>
                <Label>身高 (cm)</Label>
                <div className="flex items-center gap-4">
                    <input
                        type="range" min="100" max="220" step="0.5"
                        className="flex-1 h-4 bg-gray-200 border-2 border-black appearance-none cursor-pointer"
                        value={formData.height}
                        onChange={e => handleChange('height', e.target.value)}
                    />
                    <PixelInput
                        type="number"
                        step="0.1"
                        min="100"
                        max="220"
                        className="w-32"
                        value={formData.height}
                        onChange={e => handleChange('height', e.target.value)}
                    />
                </div>
            </div>
            <div>
                <Label>體重 (kg)</Label>
                <div className="flex items-center gap-4">
                    <input
                        type="range" min="30" max="150" step="0.01"
                        className="flex-1 h-4 bg-gray-200 border-2 border-black appearance-none cursor-pointer"
                        value={formData.weight}
                        onChange={e => handleChange('weight', e.target.value)}
                    />
                    <PixelInput
                        type="number"
                        step="0.01"
                        min="30"
                        max="150"
                        className="w-32"
                        value={formData.weight}
                        onChange={e => handleChange('weight', e.target.value)}
                    />
                </div>
            </div>
        </div>
    );

    // Step 3: Socioeconomic (Edu, Job, Money, Family)
    const renderStep3 = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold mb-4">社會經濟狀況 (3/4)</h3>

            {/* Education */}
            <div>
                <Label>最高學歷</Label>
                <div className="grid grid-cols-2 gap-2">
                    {['國小', '國中', '高中(職)', '專科', '大學', '碩士', '博士'].map(opt => (
                        <button
                            key={opt}
                            className={`py-2 px-4 border-2 border-black font-bold text-sm ${formData.education === opt ? 'bg-black text-white' : 'bg-white'}`}
                            onClick={() => handleChange('education', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            </div>

            {/* Teaching Job */}
            <div>
                <Label>目前是否有兼職或正職工作?</Label>
                <div className="flex gap-4 mb-2">
                    <button className={`flex-1 py-2 border-2 border-black ${formData.has_job === true ? 'bg-black text-white' : 'bg-white'}`} onClick={() => handleChange('has_job', true)}>有</button>
                    <button className={`flex-1 py-2 border-2 border-black ${formData.has_job === false ? 'bg-black text-white' : 'bg-white'}`} onClick={() => { handleChange('has_job', false); handleChange('salary_range', ''); }}>無</button>
                </div>
                {formData.has_job && (
                    <div className="pl-4 border-l-4 border-gray-300">
                        <Label>薪資區間</Label>
                        <select
                            className="w-full p-2 border-2 border-black"
                            value={formData.salary_range}
                            onChange={e => handleChange('salary_range', e.target.value)}
                        >
                            <option value="">請選擇</option>
                            <option value="20000以下">20000以下</option>
                            <option value="20001-35000">20001-35000</option>
                            <option value="35001-50000">35001-50000</option>
                            <option value="50001以上">50001以上</option>
                        </select>
                    </div>
                )}
            </div>

            {/* Economic Status */}
            <div>
                <div className="flex justify-between items-center">
                    <Label>家庭經濟狀況</Label>
                    <span className="text-xs text-gray-500 cursor-help" title="70萬以下為清寒、70-150萬為普通、150-300萬為小康、300萬以上為富裕">ℹ️ 說明</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                    {['清寒', '普通', '小康', '富裕'].map(opt => (
                        <button
                            key={opt}
                            className={`py-2 px-4 border-2 border-black font-bold ${formData.economic_status === opt ? 'bg-black text-white' : 'bg-white'}`}
                            onClick={() => handleChange('economic_status', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );

    // Step 4: Family Details & Religion
    const renderStep4 = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold mb-4">家庭與其他 (4/4)</h3>

            {/* Marital Status */}
            <div>
                <Label>婚姻狀況</Label>
                <div className="grid grid-cols-3 gap-2">
                    {['未婚', '已婚', '離婚', '喪偶', '其他'].map(opt => (
                        <button
                            key={opt}
                            className={`py-2 border-2 border-black text-sm ${formData.marital_status === opt ? 'bg-black text-white' : 'bg-white'}`}
                            onClick={() => handleChange('marital_status', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
                {formData.marital_status === '其他' && (
                    <PixelInput
                        value={formData.marriage_other}
                        onChange={e => handleChange('marriage_other', e.target.value)}
                        placeholder="請說明"
                        className="mt-2"
                    />
                )}
            </div>

            {/* Children */}
            <div>
                <Label>有無子女</Label>
                <div className="flex gap-4 mb-2">
                    <button className={`flex-1 py-2 border-2 border-black ${formData.has_children === true ? 'bg-black text-white' : 'bg-white'}`} onClick={() => handleChange('has_children', true)}>有</button>
                    <button className={`flex-1 py-2 border-2 border-black ${formData.has_children === false ? 'bg-black text-white' : 'bg-white'}`} onClick={() => { handleChange('has_children', false); handleChange('children_count', 0); }}>無</button>
                </div>
                {formData.has_children && (
                    <div className="pl-4 border-l-4 border-gray-300">
                        <Label>子女數量: {formData.children_count}</Label>
                        <input
                            type="range" min="1" max="10"
                            className="w-full h-4 bg-gray-200 border-2 border-black appearance-none cursor-pointer"
                            value={formData.children_count || 1}
                            onChange={e => handleChange('children_count', parseInt(e.target.value))}
                        />
                    </div>
                )}
            </div>

            {/* Family Structure */}
            <div>
                <Label>家庭結構</Label>
                <div className="grid grid-cols-2 gap-2">
                    {['雙親', '單親', '隔代教養', '其他'].map(opt => (
                        <button
                            key={opt}
                            className={`py-2 px-4 border-2 border-black font-bold text-sm ${formData.family_structure === opt ? 'bg-black text-white' : 'bg-white'}`}
                            onClick={() => handleChange('family_structure', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
                {formData.family_structure === '其他' && (
                    <PixelInput
                        value={formData.family_other}
                        onChange={e => handleChange('family_other', e.target.value)}
                        placeholder="請說明"
                        className="mt-2"
                    />
                )}
            </div>

            {/* Living Situation */}
            <div>
                <Label>居住狀況</Label>
                <div className="grid grid-cols-3 gap-2">
                    {['獨居', '與家人同住', '與他人同住'].map(opt => (
                        <button
                            key={opt}
                            className={`py-2 px-2 border-2 border-black font-bold text-sm ${formData.living_situation === opt ? 'bg-black text-white' : 'bg-white'}`}
                            onClick={() => handleChange('living_situation', opt)}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
                {(formData.living_situation === '與家人同住' || formData.living_situation === '與他人同住') && (
                    <div className="mt-2 pl-4 border-l-4 border-gray-300">
                        <Label>同住人數 (扣掉自己): {formData.cohabitant_count}</Label>
                        <input
                            type="range" min="1" max="10"
                            className="w-full h-4 bg-gray-200 border-2 border-black appearance-none cursor-pointer"
                            value={formData.cohabitant_count || 1}
                            onChange={e => handleChange('cohabitant_count', parseInt(e.target.value))}
                        />
                    </div>
                )}
            </div>

            {/* Location */}
            <div>
                <Label>居住地</Label>
                <div className="flex gap-2">
                    <PixelInput
                        value={formData.location_city}
                        onChange={e => handleChange('location_city', e.target.value)}
                        placeholder="縣市 (例: 臺北市)"
                    />
                    <PixelInput
                        value={formData.location_district}
                        onChange={e => handleChange('location_district', e.target.value)}
                        placeholder="區域 (例: 信義區)"
                    />
                </div>
            </div>

            {/* Religion */}
            <div>
                <Label>宗教信仰</Label>
                <div className="flex gap-4 mb-2">
                    <button className={`flex-1 py-2 border-2 border-black ${formData.religion === true ? 'bg-black text-white' : 'bg-white'}`} onClick={() => handleChange('religion', true)}>有</button>
                    <button className={`flex-1 py-2 border-2 border-black ${formData.religion === false ? 'bg-black text-white' : 'bg-white'}`} onClick={() => { handleChange('religion', false); handleChange('religion_other', ''); }}>無</button>
                </div>
                {formData.religion && (
                    <PixelInput
                        value={formData.religion_other}
                        onChange={e => handleChange('religion_other', e.target.value)}
                        placeholder="請填寫信仰宗教"
                    />
                )}
            </div>

        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-yellow-100 to-orange-100 py-10 px-4">
            <div className="max-w-2xl mx-auto">
                <PixelCard className="bg-white">
                    <h1 className="text-3xl font-bold mb-2 text-center">歡迎加入失樂感</h1>
                    <p className="text-gray-600 mb-8 text-center">請先完成您的個人檔案以開始使用。</p>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 h-4 border-2 border-black mb-8 rounded-full overflow-hidden">
                        <div
                            className="bg-green-500 h-full transition-all duration-300"
                            style={{ width: `${(step / 4) * 100}%` }}
                        ></div>
                    </div>

                    <div className="min-h-[400px]">
                        {step === 1 && renderStep1()}
                        {step === 2 && renderStep2()}
                        {step === 3 && renderStep3()}
                        {step === 4 && renderStep4()}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'row', gap: '10px', width: '100%', marginTop: '2rem', paddingTop: '1.5rem', borderTop: '2px solid #f3f4f6' }}>
                        {step > 1 ? (
                            <div style={{ flex: 1 }}>
                                <PixelButton onClick={prevStep} variant="secondary" style={{ width: '100%' }}>上一步</PixelButton>
                            </div>
                        ) : (
                            <div style={{ flex: 1 }} />
                        )}

                        {step < 4 ? (
                            <div style={{ flex: 1 }}>
                                <PixelButton onClick={nextStep} variant="primary" disabled={!canProceed()} style={{ width: '100%' }}>下一步</PixelButton>
                            </div>
                        ) : (
                            <div style={{ flex: 1 }}>
                                <PixelButton onClick={handleSubmit} disabled={isLoading || !canProceed()} variant="danger" style={{ width: '100%' }}>
                                    {isLoading ? '儲存中...' : '完成並開始'}
                                </PixelButton>
                            </div>
                        )}
                    </div>
                </PixelCard>
            </div>
        </div>
    );
};
