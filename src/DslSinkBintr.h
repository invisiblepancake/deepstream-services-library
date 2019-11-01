
/*
The MIT License

Copyright (c) 2019-Present, ROBERT HOWELL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in-
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#ifndef _DSL_SINK_BINTR_H
#define _DSL_SINK_BINTR_H

#include "Dsl.h"
#include "DslBintr.h"
#include "DslPadtr.h"
#include "DslElementr.h"

#define DSL_OVERLAY_SINK_PTR std::shared_ptr<DSL::OverlaySinkBintr>
#define DSL_OVERLAY_SINK_NEW(name, offsetX, offsetY, width, height) \
    std::shared_ptr<DSL::OverlaySinkBintr>( \
    new DSL::OverlaySinkBintr(name, offsetX, offsetY, width, height))

namespace DSL
{
    class SinkBintr : public Bintr
    {
    public: 
    
        SinkBintr(const char* sink)
            : Bintr(sink) 
        {
            LOG_FUNC();
        };

        ~SinkBintr()
        {
            LOG_FUNC();
        };
  
        std::shared_ptr<StaticPadtr> m_pStaticSinkPadtr;        
    };

    class OverlaySinkBintr : public SinkBintr
    {
    public: 
    
        OverlaySinkBintr(const char* sink, guint offsetX, guint offsetY, guint width, guint height);

        ~OverlaySinkBintr();
  
        std::shared_ptr<StaticPadtr> m_pStaticSinkPadtr;        
      
        void LinkAll();
        
        void UnlinkAll();

        void AddToParent(std::shared_ptr<Bintr> pParentBintr);

        int GetDisplayId()
        {
            LOG_FUNC();
            
            return m_displayId;
        }

        int GetOverlayId()
        {
            LOG_FUNC();
            
            return m_overlayId;
        }

        void SetDisplayId(int id)
        {
            LOG_FUNC();
            
            m_displayId = id;
        }

        void SetOverlayId(int id)
        {
            LOG_FUNC();
            
            m_overlayId = id;
        }

        
    private:

        boolean m_sync;
        boolean m_async;
        boolean m_qos;
        uint m_displayId;
        uint m_overlayId;
        uint m_offsetX;
        uint m_offsetY;
        uint m_width;
        uint m_height;

        DSL_ELEMENT_PTR m_pQueue;
        DSL_ELEMENT_PTR m_pTransform;
        DSL_ELEMENT_PTR m_pOverlay;
    };

}

#endif // _DSL_SINK_BINTR_H
    